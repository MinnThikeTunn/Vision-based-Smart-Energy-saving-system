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
