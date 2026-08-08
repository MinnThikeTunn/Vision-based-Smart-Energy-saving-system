from pathlib import Path
import inspect
import time
import numpy as np
from app.api.video_router import video_feed
from app.detector.pipeline import VisionPipeline
from app.detector.person_detector import DummyDetector


def dummy_capture():
    return np.zeros((480, 640, 3), dtype=np.uint8)


def test_heatmap_toggle_frontend_integration():
    """Verify that dashboard index.html correctly updates video stream URL on toggleHeatmap."""
    index_path = Path(__file__).parent.parent / "app" / "static" / "index.html"
    content = index_path.read_text(encoding="utf-8")
    # HTML must update stream src or toggle heatmap param
    assert "heatmap=true" in content or "heatmap=1" in content


def test_video_feed_accepts_heatmap_parameter():
    """Verify /api/video_feed query parameter heatmap=true is accepted by API router signature."""
    sig = inspect.signature(video_feed)
    assert "heatmap" in sig.parameters


def test_pipeline_draws_heatmap():
    """Verify VisionPipeline generates frame overlay when draw_heatmap is enabled."""
    detector = DummyDetector(fake_count=1)
    pipeline = VisionPipeline(detector=detector, capture_func=dummy_capture, fps_target=30)
    pipeline.start()
    try:
        time.sleep(0.1)
        frame_normal, _, _ = pipeline.get_latest_processed(draw_heatmap=False)
        frame_heatmap, _, _ = pipeline.get_latest_processed(draw_heatmap=True)
        assert frame_normal is not None
        assert frame_heatmap is not None
        assert not np.array_equal(frame_normal, frame_heatmap)
    finally:
        pipeline.stop()
