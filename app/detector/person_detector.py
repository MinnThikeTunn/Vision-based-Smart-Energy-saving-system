import cv2  # type: ignore[import-untyped,reportMissingImports]
import numpy as np
from app.detector.tracker import CentroidTracker

try:
    from ultralytics import YOLO  # type: ignore[import-untyped,reportMissingImports]
except ImportError:
    YOLO = None


class BaseDetector:
    def detect(self, frame: np.ndarray, spatial_zones: list | None = None) -> tuple[list[dict], int, np.ndarray]:
        """
        Returns:
            boxes: List of dicts [{'bbox': [x1, y1, x2, y2], 'confidence': float, 'id': int, 'zone': str | None}]
            count: Number of persons detected
            annotated_frame: Frame with rendered overlays (spatial zones & tracking IDs)
        """
        raise NotImplementedError


def draw_spatial_zones(frame: np.ndarray, spatial_zones: list | None = None) -> np.ndarray:
    """Draw custom spatial zones on the video frame."""
    annotated = frame.copy()
    h, w = annotated.shape[:2]

    if spatial_zones and len(spatial_zones) > 0:
        colors = [(255, 200, 0), (255, 0, 200), (0, 220, 255), (100, 255, 100)]
        for idx, zone in enumerate(spatial_zones):
            b = zone.bbox if hasattr(zone, "bbox") else zone.get("bbox", [0, 0, 1, 1])
            name = zone.name if hasattr(zone, "name") else zone.get("name", f"Zone {idx+1}")
            x1, y1 = int(b[0] * w), int(b[1] * h)
            x2, y2 = int(b[2] * w), int(b[3] * h)
            color = colors[idx % len(colors)]

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated,
                name,
                (x1 + 10, max(20, y1 + 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

    return annotated


def match_box_to_zone(
    bbox: list[float],
    w: int,
    h: int,
    spatial_zones: list | None,
    min_overlap_ratio: float = 0.3,
) -> str | None:
    """
    Find which spatial zone contains at least min_overlap_ratio (default 30%) of the person's bounding box area.
    If multiple zones satisfy min_overlap_ratio, returns the zone with the highest overlap ratio.
    """
    if not spatial_zones or not bbox or len(bbox) < 4:
        return None

    px1, py1, px2, py2 = bbox[:4]
    person_area = max(0.0, px2 - px1) * max(0.0, py2 - py1)
    if person_area <= 0:
        return None

    best_zone_name = None
    best_overlap_ratio = 0.0

    for zone in spatial_zones:
        b = zone.bbox if hasattr(zone, "bbox") else zone.get("bbox", [0, 0, 1, 1])
        name = zone.name if hasattr(zone, "name") else zone.get("name", "Zone")
        if len(b) >= 4:
            zx1, zy1 = b[0] * w, b[1] * h
            zx2, zy2 = b[2] * w, b[3] * h

            ix1 = max(px1, zx1)
            iy1 = max(py1, zy1)
            ix2 = min(px2, zx2)
            iy2 = min(py2, zy2)

            inter_area = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
            overlap_ratio = inter_area / person_area

            if overlap_ratio >= min_overlap_ratio and overlap_ratio > best_overlap_ratio:
                best_overlap_ratio = overlap_ratio
                best_zone_name = name

    return best_zone_name


def match_point_to_zone(cx: int, cy: int, w: int, h: int, spatial_zones: list | None) -> str | None:
    """Legacy wrapper maintained for backwards compatibility."""
    return match_box_to_zone([cx - 5, cy - 5, cx + 5, cy + 5], w, h, spatial_zones, min_overlap_ratio=0.01)


class DummyDetector(BaseDetector):
    def __init__(self, fake_count: int = 1):
        self.fake_count = fake_count
        self.tracker = CentroidTracker()

    def detect(self, frame: np.ndarray, spatial_zones: list | None = None) -> tuple[list[dict], int, np.ndarray]:
        annotated = draw_spatial_zones(frame, spatial_zones=spatial_zones)
        h, w = frame.shape[:2]
        raw_rects = []
        if self.fake_count > 0:
            x1, y1, x2, y2 = int(w * 0.2), int(h * 0.2), int(w * 0.6), int(h * 0.8)
            raw_rects.append([float(x1), float(y1), float(x2), float(y2)])

        tracked_objects = self.tracker.update(raw_rects)

        boxes = []
        for obj_id, data in tracked_objects.items():
            x1, y1, x2, y2, cx, cy = map(int, data)
            zone = match_box_to_zone([x1, y1, x2, y2], w, h, spatial_zones, min_overlap_ratio=0.3)
            label = f"ID #{obj_id} [{zone}]" if zone else f"ID #{obj_id}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(annotated, (cx, cy), 4, (0, 255, 255), -1)
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
            boxes.append({"bbox": [x1, y1, x2, y2], "confidence": 0.95, "id": obj_id, "zone": zone})

        count = len(tracked_objects)
        cv2.putText(
            annotated,
            f"Occupants: {count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0) if count > 0 else (0, 0, 255),
            2,
        )
        return boxes, count, annotated


class YOLOPersonDetector(BaseDetector):
    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        device: str = "cpu",
    ):
        if YOLO is None:
            raise RuntimeError("ultralytics package is required for YOLOPersonDetector")
        self.model = YOLO(model_name)
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.tracker = CentroidTracker()

    def detect(self, frame: np.ndarray, spatial_zones: list | None = None) -> tuple[list[dict], int, np.ndarray]:
        results = self.model(
            frame,
            verbose=False,
            device=self.device,
            conf=self.confidence_threshold,
        )
        annotated = draw_spatial_zones(frame, spatial_zones=spatial_zones)
        h, w = frame.shape[:2]

        raw_rects = []
        if len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes:
                cls_id = int(box.cls[0].item())
                if cls_id == 0:  # Person class
                    xyxy = box.xyxy[0].cpu().numpy().astype(float)
                    raw_rects.append([xyxy[0], xyxy[1], xyxy[2], xyxy[3]])

        tracked_objects = self.tracker.update(raw_rects)

        boxes = []
        for obj_id, data in tracked_objects.items():
            x1, y1, x2, y2, cx, cy = map(int, data)
            zone = match_box_to_zone([x1, y1, x2, y2], w, h, spatial_zones, min_overlap_ratio=0.3)
            label = f"ID #{obj_id} [{zone}]" if zone else f"ID #{obj_id}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(annotated, (cx, cy), 4, (0, 255, 255), -1)
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
            boxes.append({"bbox": [x1, y1, x2, y2], "confidence": 0.90, "id": obj_id, "zone": zone})

        count = len(tracked_objects)
        cv2.putText(
            annotated,
            f"Occupants: {count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0) if count > 0 else (0, 0, 255),
            2,
        )

        return boxes, count, annotated
