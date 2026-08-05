from typing import Optional
import cv2
from fastapi import APIRouter
from fastapi.responses import Response, StreamingResponse
import numpy as np

from app.detector.pipeline import VisionPipeline

router = APIRouter(prefix="/api", tags=["video"])

_pipeline_instance: Optional[VisionPipeline] = None


def get_vision_pipeline() -> VisionPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        from app.config.loader import load_settings
        from app.detector.person_detector import DummyDetector, YOLOPersonDetector

        settings = load_settings()
        detector_cfg = settings.detector
        camera_cfg = settings.camera

        try:
            detector = YOLOPersonDetector(
                model_name=detector_cfg.model_name,
                confidence_threshold=detector_cfg.confidence_threshold,
                device=detector_cfg.device,
            )
            print(f"Successfully loaded YOLOPersonDetector using model {detector_cfg.model_name}")
        except Exception as e:
            print(f"Failed to load YOLO detector, falling back to DummyDetector: {e}")
            detector = DummyDetector()

        _pipeline_instance = VisionPipeline(
            detector=detector,
            camera_index=camera_cfg.index,
            fps_target=camera_cfg.fps,
            anonymize_faces=settings.privacy.anonymize_faces,
        )
        _pipeline_instance.start()
    else:
        from app.config.loader import load_settings
        from app.detector.person_detector import YOLOPersonDetector
        try:
            settings = load_settings()
            if isinstance(_pipeline_instance.detector, YOLOPersonDetector):
                _pipeline_instance.detector.confidence_threshold = settings.detector.confidence_threshold
                _pipeline_instance.detector.device = settings.detector.device
            _pipeline_instance.anonymize_faces = settings.privacy.anonymize_faces
        except Exception:
            pass

    return _pipeline_instance


def set_vision_pipeline(pipeline: VisionPipeline) -> None:
    global _pipeline_instance
    _pipeline_instance = pipeline


@router.get("/video_feed")
def video_feed():
    from app.config.loader import load_settings
    settings = load_settings()
    
    # Headless Automation Mode: disable video stream if configured
    if settings.privacy.headless_mode:
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(
            placeholder,
            "Headless Mode Active",
            (170, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 200),
            2,
        )
        cv2.putText(
            placeholder,
            "(Video Stream Disabled for Privacy)",
            (120, 260),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (200, 200, 200),
            1,
        )
        _, jpeg = cv2.imencode(".jpg", placeholder)
        return Response(content=jpeg.tobytes(), media_type="image/jpeg")

    pipeline = get_vision_pipeline()
    return StreamingResponse(
        pipeline.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
