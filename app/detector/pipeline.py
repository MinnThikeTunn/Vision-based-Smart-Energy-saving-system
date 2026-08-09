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

        self.is_running: bool = False
        self._capture_thread: threading.Thread | None = None
        self._inference_thread: threading.Thread | None = None
        self._cap: cv2.VideoCapture | None = None

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

    def _capture_loop(self) -> None:
        frame_interval = 1.0 / self.fps_target
        while self.is_running:
            start_time = time.time()
            frame = None
            if self.custom_capture_func is not None:
                frame = self.custom_capture_func()
            elif self._cap is not None and self._cap.isOpened():
                ret, frame = self._cap.read()
                if not ret:
                    frame = None

            if frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(
                    frame,
                    "No Camera Feed",
                    (200, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            with self._lock:
                self._raw_frame = frame

            elapsed = time.time() - start_time
            sleep_time = max(0.001, frame_interval - elapsed)
            time.sleep(sleep_time)

    def _apply_anonymization(self, frame: np.ndarray, boxes: list) -> np.ndarray:
        """Apply Gaussian blur over detected person regions for privacy canvas anonymization."""
        anonymized = frame.copy()
        h, w = anonymized.shape[:2]
        for box in boxes:
            b = box.get("bbox") if isinstance(box, dict) else box
            if b and len(b) >= 4:
                x1, y1, x2, y2 = map(int, b[:4])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1:
                    roi = anonymized[y1:y2, x1:x2]
                    ksize = (max(31, (x2 - x1) // 2 | 1), max(31, (y2 - y1) // 2 | 1))
                    anonymized[y1:y2, x1:x2] = cv2.GaussianBlur(roi, ksize, 30)
        return anonymized

    def _inference_loop(self) -> None:
        while self.is_running:
            frame_to_process = None
            with self._lock:
                if self._raw_frame is not None:
                    frame_to_process = self._raw_frame.copy()

            if frame_to_process is not None:
                boxes, count, annotated = self.detector.detect(frame_to_process)

                if self.anonymize_faces and len(boxes) > 0:
                    annotated = self._apply_anonymization(annotated, boxes)

                active_zones = list(set(b["zone"] for b in boxes if isinstance(b, dict) and "zone" in b))

                with self._lock:
                    self._processed_frame = annotated
                    self._occupant_count = count
                    self._boxes = boxes
                    self._active_zones = active_zones

            time.sleep(1.0 / self.fps_target)

    def get_latest_processed(self, draw_heatmap: bool = False) -> tuple[np.ndarray | None, int, list[str]]:
        with self._lock:
            frame = self._processed_frame.copy() if self._processed_frame is not None else None
            if frame is not None and draw_heatmap:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                heatmap_overlay = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
                frame = cv2.addWeighted(frame, 0.7, heatmap_overlay, 0.3, 0)
            return frame, self._occupant_count, list(self._active_zones)

    def generate_mjpeg_stream(self, draw_heatmap: bool = False):
        while self.is_running:
            frame, _, _ = self.get_latest_processed(draw_heatmap=draw_heatmap)
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

