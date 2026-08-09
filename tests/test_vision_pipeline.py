import time
import numpy as np
import pytest
from app.detector.person_detector import BaseDetector, DummyDetector
from app.detector.pipeline import VisionPipeline


def test_dummy_detector():
    detector = DummyDetector()
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    boxes, count, annotated = detector.detect(fake_frame)

    assert isinstance(count, int)
    assert count >= 0
    assert annotated.shape == fake_frame.shape


def test_vision_pipeline_lifecycle():
    def dummy_capture():
        return np.zeros((480, 640, 3), dtype=np.uint8)

    pipeline = VisionPipeline(detector=DummyDetector(), capture_func=dummy_capture)
    pipeline.start()
    time.sleep(0.2)

    assert pipeline.is_running
    latest_frame, count, active_zones = pipeline.get_latest_processed()
    assert count >= 0
    assert latest_frame is not None
    assert isinstance(active_zones, list)

    pipeline.stop()
    assert not pipeline.is_running


def test_mjpeg_stream_generator():
    def dummy_capture():
        return np.zeros((100, 100, 3), dtype=np.uint8)

    pipeline = VisionPipeline(detector=DummyDetector(), capture_func=dummy_capture)
    pipeline.start()

    stream_gen = pipeline.generate_mjpeg_stream()
    frame_bytes = next(stream_gen)

    assert b"--frame" in frame_bytes
    assert b"Content-Type: image/jpeg" in frame_bytes

    pipeline.stop()


def test_yolo_person_detector():
    from app.detector.person_detector import YOLOPersonDetector
    detector = YOLOPersonDetector()
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    boxes, count, annotated = detector.detect(fake_frame)

    assert isinstance(count, int)
    assert count >= 0
    assert annotated.shape == fake_frame.shape


def test_zero_zone_default_and_custom_zone_matching():
    from app.config.schema import SpatialZoneConfig
    from app.detector.person_detector import DummyDetector, draw_spatial_zones

    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # 1. When spatial_zones is empty, draw_spatial_zones should not draw hardcoded fallback zones
    annotated_empty = draw_spatial_zones(fake_frame, spatial_zones=[])
    # Comparing image equality: empty frame vs annotated_empty should be equal (no overlays drawn)
    np.testing.assert_array_equal(annotated_empty, fake_frame)

    # 2. When spatial_zones is empty, DummyDetector with fake occupant should return zone=None or unassigned
    detector = DummyDetector(fake_count=1)
    boxes, count, annotated = detector.detect(fake_frame, spatial_zones=[])
    assert len(boxes) == 1
    assert boxes[0]["zone"] is None

    # 3. When custom spatial_zone is provided, occupant in zone bbox should match zone name
    # Fake occupant center is around cx=0.4*640=256, cy=0.5*480=240
    custom_zone = SpatialZoneConfig(name="Desk Zone", bbox=[0.1, 0.1, 0.7, 0.9])
    boxes, count, annotated = detector.detect(fake_frame, spatial_zones=[custom_zone])
    assert len(boxes) == 1
    assert boxes[0]["zone"] == "Desk Zone"


