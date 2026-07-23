from typing import Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.detector.pipeline import VisionPipeline

router = APIRouter(prefix="/api", tags=["video"])

_pipeline_instance: Optional[VisionPipeline] = None


def get_vision_pipeline() -> VisionPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        from app.config.loader import load_settings
        from app.detector.person_detector import YOLOPersonDetector, DummyDetector

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
        )
        _pipeline_instance.start()
    else:
        # Dynamically sync settings that can be updated on the fly
        from app.config.loader import load_settings
        from app.detector.person_detector import YOLOPersonDetector
        try:
            settings = load_settings()
            if isinstance(_pipeline_instance.detector, YOLOPersonDetector):
                _pipeline_instance.detector.confidence_threshold = settings.detector.confidence_threshold
                _pipeline_instance.detector.device = settings.detector.device
        except Exception:
            pass

    return _pipeline_instance


def set_vision_pipeline(pipeline: VisionPipeline) -> None:
    global _pipeline_instance
    _pipeline_instance = pipeline


@router.get("/video_feed")
def video_feed():
    pipeline = get_vision_pipeline()
    return StreamingResponse(
        pipeline.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
