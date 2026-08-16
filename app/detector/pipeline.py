from collections.abc import Callable
import contextlib
import sys
import threading
import time
import cv2
import numpy as np
from app.detector.person_detector import BaseDetector, DummyDetector


class VisionPipeline:
    def __init__(
        self,
        detector: BaseDetector | None = None,
        camera_index: int = 0,
        capture_func: Callable[[], np.ndarray | None] | None = None,
        fps_target: int = 30,
        anonymize_faces: bool = False,
    ):
        self.detector = detector or DummyDetector()
        self.camera_index = camera_index
        self.custom_capture_func = capture_func
        self.fps_target = fps_target
        self.anonymize_faces = anonymize_faces

        self._lock = threading.Lock()
        self._raw_frame: np.ndarray | None = None
        self._processed_frame: np.ndarray | None = None
        self._occupant_count: int = 0
        self._boxes: list = []
        self._active_zones: list[str] = []

        # Multi-Channel Heatmap Accumulator Buffers & Config
        self._acc_instant: np.ndarray | None = None
        self._acc_5m: np.ndarray | None = None
        self._acc_session: np.ndarray | None = None
        self.max_saturation_sec: float = 300.0

        # Temporal Decay Factors (per frame tick at ~30 FPS)
        self.alpha_instant: float = 0.95
        self.alpha_5m: float = 0.998
        self.alpha_session: float = 0.9999

        self.is_running: bool = False
        self._capture_thread: threading.Thread | None = None
        self._inference_thread: threading.Thread | None = None
        self._cap: cv2.VideoCapture | None = None

        # Pre-Allocated Static Zero-Copy Frame Buffers
        self._raw_buf: np.ndarray | None = None
        self._processed_buf: np.ndarray | None = None
        self._infer_buf: np.ndarray | None = None
        self._anonymize_buf: np.ndarray | None = None
        self._out_buf: np.ndarray | None = None

    def start(self) -> None:
        if self.is_running:
            return

        self.is_running = True
        if self.custom_capture_func is None:
            backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
            with contextlib.suppress(Exception):
                self._cap = cv2.VideoCapture(self.camera_index, backend)

        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._inference_thread = threading.Thread(target=self._inference_loop, daemon=True)

        self._capture_thread.start()
        self._inference_thread.start()

    def stop(self) -> None:
        self.is_running = False
        if self._cap is not None:
            with contextlib.suppress(Exception):
                self._cap.release()
            self._cap = None

    def _ensure_buffer(self, buf: np.ndarray | None, shape: tuple[int, ...], dtype=np.uint8) -> np.ndarray:
        """Ensure static pre-allocated buffer matches required shape without dynamic GC churn."""
        if buf is None or buf.shape != shape or buf.dtype != dtype:
            return np.zeros(shape, dtype=dtype)
        return buf

    def _capture_loop(self) -> None:
        frame_interval = 1.0 / self.fps_target
        consecutive_drops = 0

        while self.is_running:
            start_time = time.time()
            frame = None

            if self.custom_capture_func is not None:
                frame = self.custom_capture_func()
            elif self._cap is not None and self._cap.isOpened():
                try:
                    ret, raw_frame = self._cap.read()
                    if ret and raw_frame is not None and raw_frame.size > 0:
                        frame = raw_frame
                        consecutive_drops = 0
                    else:
                        frame = None
                except Exception:
                    frame = None

            # Camera Resilience Watchdog: handle disconnects with exponential backoff & auto-reconnect
            if frame is None and self.custom_capture_func is None:
                consecutive_drops += 1
                synthetic_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                msg = f"Camera Reconnecting (Attempt {consecutive_drops})..."
                cv2.putText(synthetic_frame, msg, (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 180, 255), 2)
                cv2.circle(synthetic_frame, (320, 280), 8, (0, 200, 255), -1)

                with self._lock:
                    self._raw_buf = self._ensure_buffer(self._raw_buf, synthetic_frame.shape)
                    np.copyto(self._raw_buf, synthetic_frame)
                    self._raw_frame = self._raw_buf

                # Exponential backoff auto-reconnect attempt
                backoff = min(5.0, 0.5 * (1.4 ** min(8, consecutive_drops)))
                time.sleep(backoff)

                if self._cap is not None:
                    with contextlib.suppress(Exception):
                        self._cap.release()
                    self._cap = None

                backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
                with contextlib.suppress(Exception):
                    self._cap = cv2.VideoCapture(self.camera_index, backend)
                continue

            elif frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "No Camera Feed", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            with self._lock:
                self._raw_buf = self._ensure_buffer(self._raw_buf, frame.shape)
                np.copyto(self._raw_buf, frame)
                self._raw_frame = self._raw_buf

            elapsed = time.time() - start_time
            sleep_time = max(0.001, frame_interval - elapsed)
            time.sleep(sleep_time)

    def _apply_anonymization(self, frame: np.ndarray, boxes: list) -> np.ndarray:
        """Apply Gaussian blur over detected person regions for privacy canvas anonymization using static buffer."""
        h, w = frame.shape[:2]
        self._anonymize_buf = self._ensure_buffer(self._anonymize_buf, frame.shape)
        np.copyto(self._anonymize_buf, frame)

        for box in boxes:
            b = box.get("bbox") if isinstance(box, dict) else box
            if b and len(b) >= 4:
                x1, y1, x2, y2 = map(int, b[:4])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1:
                    roi = self._anonymize_buf[y1:y2, x1:x2]
                    ksize = (max(31, (x2 - x1) // 2 | 1), max(31, (y2 - y1) // 2 | 1))
                    self._anonymize_buf[y1:y2, x1:x2] = cv2.GaussianBlur(roi, ksize, 30)
        return self._anonymize_buf

    def _splat_footprints(self, frame_shape: tuple[int, int], boxes: list) -> None:
        """Splat Gaussian density at person footprint centers (x_c, y_max) into multi-channel accumulators."""
        h, w = frame_shape[:2]
        if self._acc_instant is None or self._acc_instant.shape != (h, w):
            self._acc_instant = np.zeros((h, w), dtype=np.float32)
            self._acc_5m = np.zeros((h, w), dtype=np.float32)
            self._acc_session = np.zeros((h, w), dtype=np.float32)

        # 1. Temporal decay on all channels
        self._acc_instant *= self.alpha_instant
        self._acc_5m *= self.alpha_5m
        self._acc_session *= self.alpha_session

        # 2. Gaussian splatting per detected footprint center
        sigma = 25
        for box in boxes:
            b = box.get("bbox") if isinstance(box, dict) else box
            if b and len(b) >= 4:
                x1, y1, x2, y2 = map(int, b[:4])
                cx = (x1 + x2) // 2
                cy = y2  # Floor footprint center

                x_min, x_max = max(0, cx - 3 * sigma), min(w, cx + 3 * sigma + 1)
                y_min, y_max = max(0, cy - 3 * sigma), min(h, cy + 3 * sigma + 1)

                if x_max > x_min and y_max > y_min:
                    y_grid, x_grid = np.ogrid[y_min:y_max, x_min:x_max]
                    gaussian = np.exp(-((x_grid - cx) ** 2 + (y_grid - cy) ** 2) / (2 * sigma ** 2))

                    self._acc_instant[y_min:y_max, x_min:x_max] += gaussian
                    self._acc_5m[y_min:y_max, x_min:x_max] += gaussian
                    self._acc_session[y_min:y_max, x_min:x_max] += gaussian

    def _inference_loop(self) -> None:
        while self.is_running:
            frame_to_process = None
            with self._lock:
                if self._raw_frame is not None:
                    self._infer_buf = self._ensure_buffer(self._infer_buf, self._raw_frame.shape)
                    np.copyto(self._infer_buf, self._raw_frame)
                    frame_to_process = self._infer_buf

            if frame_to_process is not None:
                spatial_zones = []
                try:
                    from app.config.loader import load_settings
                    spatial_zones = load_settings().spatial_zones
                except Exception:
                    pass

                boxes, count, annotated = self.detector.detect(frame_to_process, spatial_zones=spatial_zones)

                if self.anonymize_faces and len(boxes) > 0:
                    annotated = self._apply_anonymization(annotated, boxes)

                active_zones = list(set(b["zone"] for b in boxes if isinstance(b, dict) and b.get("zone")))

                with self._lock:
                    self._splat_footprints(frame_to_process.shape, boxes)
                    self._processed_buf = self._ensure_buffer(self._processed_buf, annotated.shape)
                    np.copyto(self._processed_buf, annotated)
                    self._processed_frame = self._processed_buf
                    self._occupant_count = count
                    self._boxes = boxes
                    self._active_zones = active_zones

            time.sleep(1.0 / self.fps_target)

    def _get_accumulator_matrix(self, window: str = "instant") -> np.ndarray | None:
        if window == "5m":
            return self._acc_5m
        elif window == "session":
            return self._acc_session
        return self._acc_instant

    def get_latest_processed(
        self,
        draw_heatmap: bool = False,
        window: str = "instant",
        alpha: float = 0.3,
    ) -> tuple[np.ndarray | None, int, list[str]]:
        with self._lock:
            frame = None
            if self._processed_frame is not None:
                self._out_buf = self._ensure_buffer(self._out_buf, self._processed_frame.shape)
                np.copyto(self._out_buf, self._processed_frame)
                frame = self._out_buf

            if frame is not None and draw_heatmap:
                acc_map = self._get_accumulator_matrix(window)
                if acc_map is not None:
                    norm = np.clip((acc_map / self.max_saturation_sec) * 255.0, 0, 255).astype(np.uint8)
                    heatmap_overlay = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
                    frame_alpha = max(0.0, min(1.0, 1.0 - alpha))
                    overlay_alpha = max(0.0, min(1.0, alpha))
                    frame = cv2.addWeighted(frame, frame_alpha, heatmap_overlay, overlay_alpha, 0)
            return frame, self._occupant_count, list(self._active_zones)

    def get_zone_heatmap_stats(
        self,
        spatial_zones: list | None = None,
        window: str = "5m",
        density_threshold: float = 0.1,
    ) -> dict[str, float]:
        """Calculate spatial utilization rate (% of zone area with active heat) for each spatial zone."""
        with self._lock:
            acc_map = self._get_accumulator_matrix(window)
            if acc_map is None:
                return {}

            h, w = acc_map.shape[:2]
            stats = {}
            if not spatial_zones:
                active_pixels = np.sum(acc_map > density_threshold)
                stats["overall"] = round(float((active_pixels / (h * w)) * 100.0), 2)
                return stats

            for idx, zone in enumerate(spatial_zones):
                z_name = getattr(zone, "name", None) or (zone.get("name") if isinstance(zone, dict) else f"Zone {idx+1}")
                points = getattr(zone, "points", None) or (zone.get("points") if isinstance(zone, dict) else None)
                bbox = getattr(zone, "bbox", None) or (zone.get("bbox") if isinstance(zone, dict) else None)

                if points and len(points) >= 3:
                    pts = np.array(points, dtype=np.int32)
                    mask = np.zeros((h, w), dtype=np.uint8)
                    cv2.fillPoly(mask, [pts], 255)
                    zone_area = np.sum(mask > 0)
                    if zone_area > 0:
                        active_in_zone = np.sum((acc_map > density_threshold) & (mask > 0))
                        stats[z_name] = round(float((active_in_zone / zone_area) * 100.0), 2)
                    else:
                        stats[z_name] = 0.0
                elif bbox and len(bbox) >= 4:
                    if max(bbox) <= 1.0:
                        x1, y1 = int(bbox[0] * w), int(bbox[1] * h)
                        x2, y2 = int(bbox[2] * w), int(bbox[3] * h)
                    else:
                        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                    x1, y1 = max(0, min(w, x1)), max(0, min(h, y1))
                    x2, y2 = max(0, min(w, x2)), max(0, min(h, y2))
                    if x2 > x1 and y2 > y1:
                        zone_acc = acc_map[y1:y2, x1:x2]
                        zone_area = (y2 - y1) * (x2 - x1)
                        active_in_zone = np.sum(zone_acc > density_threshold)
                        stats[z_name] = round(float((active_in_zone / zone_area) * 100.0), 2)
                    else:
                        stats[z_name] = 0.0
                else:
                    stats[z_name] = 0.0

            active_pixels = np.sum(acc_map > density_threshold)
            stats["overall"] = round(float((active_pixels / (h * w)) * 100.0), 2)
            return stats

    def reset_heatmap_accumulator(self, window: str = "all") -> None:
        with self._lock:
            if self._acc_instant is not None:
                if window in ("instant", "all"):
                    self._acc_instant.fill(0)
                if window in ("5m", "all") and self._acc_5m is not None:
                    self._acc_5m.fill(0)
                if window in ("session", "all") and self._acc_session is not None:
                    self._acc_session.fill(0)

    def generate_mjpeg_stream(
        self,
        draw_heatmap: bool = False,
        window: str = "instant",
        alpha: float = 0.3,
    ):
        while self.is_running:
            frame, _, _ = self.get_latest_processed(
                draw_heatmap=draw_heatmap, window=window, alpha=alpha
            )
            if frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(
                    frame,
                    "Connecting Camera...",
                    (180, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            ret, jpeg = cv2.imencode(".jpg", frame)
            if ret:
                frame_bytes = jpeg.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
            time.sleep(1.0 / self.fps_target)

