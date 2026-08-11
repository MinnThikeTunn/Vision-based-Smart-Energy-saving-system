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
    assert "heatmap=true" in content or "heatmap=1" in content


def test_video_feed_accepts_heatmap_parameter():
    """Verify /api/video_feed query parameters are accepted by API router signature."""
    sig = inspect.signature(video_feed)
    assert "heatmap" in sig.parameters
    assert "window" in sig.parameters
    assert "alpha" in sig.parameters


def test_pipeline_draws_heatmap():
    """Verify VisionPipeline generates frame overlay when draw_heatmap is enabled."""
    detector = DummyDetector(fake_count=1)
    pipeline = VisionPipeline(detector=detector, capture_func=dummy_capture, fps_target=30)
    pipeline.start()
    try:
        time.sleep(0.4)
        frame_normal, _, _ = pipeline.get_latest_processed(draw_heatmap=False)
        frame_heatmap, _, _ = pipeline.get_latest_processed(draw_heatmap=True, window="5m", alpha=0.4)
        assert frame_normal is not None
        assert frame_heatmap is not None
        assert not np.array_equal(frame_normal, frame_heatmap)
    finally:
        pipeline.stop()


def test_multi_channel_buffers_and_splatting():
    """Verify multi-channel accumulators splat footprints and maintain separate channels."""
    pipeline = VisionPipeline(capture_func=dummy_capture, fps_target=30)
    boxes = [{"bbox": [100, 50, 200, 250]}]
    pipeline._splat_footprints((480, 640, 3), boxes)

    assert pipeline._acc_instant is not None
    assert pipeline._acc_5m is not None
    assert pipeline._acc_session is not None

    # Footprint center: cx = 150, cy = 250
    cx, cy = 150, 250
    assert pipeline._acc_instant[cy, cx] > 0.5
    assert pipeline._acc_5m[cy, cx] > 0.5
    assert pipeline._acc_session[cy, cx] > 0.5


def test_zone_heatmap_stats_and_reset():
    """Verify spatial utilization calculation per zone and reset functionality."""
    pipeline = VisionPipeline(capture_func=dummy_capture, fps_target=30)
    boxes = [{"bbox": [100, 100, 200, 300]}]
    pipeline._splat_footprints((480, 640, 3), boxes)

    zones = [
        {
            "name": "Zone A",
            "points": [[80, 80], [220, 80], [220, 320], [80, 320]],
        }
    ]

    stats = pipeline.get_zone_heatmap_stats(spatial_zones=zones, window="instant")
    assert "Zone A" in stats
    assert stats["Zone A"] > 0.0
    assert "overall" in stats

    # Reset accumulator
    pipeline.reset_heatmap_accumulator(window="all")
    stats_after = pipeline.get_zone_heatmap_stats(spatial_zones=zones, window="instant")
    assert stats_after["Zone A"] == 0.0


def test_export_heatmap_endpoint():
    """Verify export_heatmap endpoint generates valid PNG image response."""
    from app.api.video_router import export_heatmap
    response = export_heatmap(window="5m")
    assert response.status_code == 200
    assert response.media_type == "image/png"
    assert len(response.body) > 100
