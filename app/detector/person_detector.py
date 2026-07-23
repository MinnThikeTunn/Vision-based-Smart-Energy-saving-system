import cv2  # type: ignore[import-untyped,reportMissingImports]
import numpy as np

try:
    from ultralytics import YOLO  # type: ignore[import-untyped,reportMissingImports]
except ImportError:
    YOLO = None


class BaseDetector:
    def detect(self, frame: np.ndarray) -> tuple[list[dict], int, np.ndarray]:
        """
        Returns:
            boxes: List of dicts [{'bbox': [x1, y1, x2, y2], 'confidence': float}]
            count: Number of persons detected
            annotated_frame: Frame with rendered overlays
        """
        raise NotImplementedError


class DummyDetector(BaseDetector):
    def __init__(self, fake_count: int = 1):
        self.fake_count = fake_count

    def detect(self, frame: np.ndarray) -> tuple[list[dict], int, np.ndarray]:
        annotated = frame.copy()
        h, w = frame.shape[:2]
        boxes = []
        if self.fake_count > 0:
            x1, y1, x2, y2 = int(w * 0.2), int(h * 0.2), int(w * 0.6), int(h * 0.8)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                "Person 0.95",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
            boxes.append({"bbox": [x1, y1, x2, y2], "confidence": 0.95})

        cv2.putText(
            annotated,
            f"Occupants: {self.fake_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0) if self.fake_count > 0 else (0, 0, 255),
            2,
        )
        return boxes, self.fake_count, annotated


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

    def detect(self, frame: np.ndarray) -> tuple[list[dict], int, np.ndarray]:
        results = self.model(
            frame,
            verbose=False,
            device=self.device,
            conf=self.confidence_threshold,
        )
        annotated = frame.copy()

        boxes = []
        count = 0
        if len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                if cls_id == 0:
                    count += 1
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = xyxy[0], xyxy[1], xyxy[2], xyxy[3]
                    boxes.append({"bbox": [x1, y1, x2, y2], "confidence": conf})

                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        annotated,
                        f"Person {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

        cv2.putText(
            annotated,
            f"Occupants: {count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0) if count > 0 else (0, 0, 255),
            2,
        )

        return boxes, count, annotated
