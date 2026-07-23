from typing import Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.detector.pipeline import VisionPipeline

router = APIRouter(prefix="/api", tags=["video"])

_pipeline_instance: Optional[VisionPipeline] = None


def get_vision_pipeline() -> VisionPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = VisionPipeline()
        _pipeline_instance.start()
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
