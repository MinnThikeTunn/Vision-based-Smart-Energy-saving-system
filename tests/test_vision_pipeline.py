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


def test_zone_entry_determined_by_overlap_percentage():
    from app.config.schema import SpatialZoneConfig
    from app.detector.person_detector import match_box_to_zone

    spatial_zones = [
        SpatialZoneConfig(name="Zone A", bbox=[0.0, 0.0, 0.5, 1.0]),
        SpatialZoneConfig(name="Zone B", bbox=[0.4, 0.0, 1.0, 1.0]),
    ]
    w, h = 100, 100

    # Test Case 1: Center (cx=62.5) is outside Zone A (ends at 50), but 33.3% of person is inside Zone A.
    # Person bbox = [25, 0, 100, 100]. Overlap with Zone A = (50-25)*100 = 2500. Total Area = 75*100 = 7500. Ratio = 33.3% >= 30%.
    # Overlap with Zone B = (100-40)*100 = 6000. Total Area = 7500. Ratio = 6000/7500 = 80.0% >= 30%.
    # Zone B has 80% overlap vs Zone A's 33.3%, so Zone B wins.
    zone_matched = match_box_to_zone([25, 0, 100, 100], w, h, spatial_zones, min_overlap_ratio=0.3)
    assert zone_matched == "Zone B"

    # Test Case 2: Person bbox = [25, 0, 45, 100]. Total area = 20*100 = 2000.
    # Overlap with Zone A (0 to 50): 20*100 = 2000 (100% overlap).
    # Overlap with Zone B (40 to 100): (45-40)*100 = 500 (25% overlap, < 30%).
    # Zone A wins with 100% overlap.
    zone_matched_a = match_box_to_zone([25, 0, 45, 100], w, h, spatial_zones, min_overlap_ratio=0.3)
    assert zone_matched_a == "Zone A"

    # Test Case 3: Person bbox = [42, 0, 48, 100]. Total area = 6*100 = 600.
    # Overlap with Zone A (0 to 50): (48-42)*100 = 600 (100%).
    # Overlap with Zone B (40 to 100): (48-42)*100 = 600 (100%).
    # Both have 100% overlap, but first evaluated or highest ratio matches.
    # Let's test a case where overlap is under 30% for all zones:
    # Zone C: bbox [0.8, 0.0, 1.0, 1.0] (80 to 100)
    # Person bbox = [0, 0, 100, 100] (100% frame). Overlap with Zone C = 20%. Under 30% threshold => None.
    spatial_zones_c = [SpatialZoneConfig(name="Zone C", bbox=[0.8, 0.0, 1.0, 1.0])]
    zone_below_thresh = match_box_to_zone([0, 0, 100, 100], w, h, spatial_zones_c, min_overlap_ratio=0.3)
    assert zone_below_thresh is None



