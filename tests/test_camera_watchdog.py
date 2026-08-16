import numpy as np
from app.detector.pipeline import VisionPipeline
from app.detector.person_detector import DummyDetector


def test_zero_copy_buffer_reuse():
    pipeline = VisionPipeline(detector=DummyDetector(), fps_target=30)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    buf = pipeline._ensure_buffer(None, fake_frame.shape)
    assert buf.shape == (480, 640, 3)

    # Reusing the buffer should return the identical object without re-allocation
    buf2 = pipeline._ensure_buffer(buf, fake_frame.shape)
    assert buf2 is buf


def test_anonymization_buffer_memory():
    pipeline = VisionPipeline(detector=DummyDetector(), anonymize_faces=True)
    fake_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
    boxes = [{"bbox": [50, 50, 150, 150]}]

    anonymized = pipeline._apply_anonymization(fake_frame, boxes)
    assert anonymized.shape == (480, 640, 3)
    assert pipeline._anonymize_buf is anonymized


def test_pipeline_custom_capture():
    frame_count = 0

    def mock_capture():
        nonlocal frame_count
        frame_count += 1
        return np.zeros((480, 640, 3), dtype=np.uint8)

    pipeline = VisionPipeline(
        detector=DummyDetector(fake_count=1),
        capture_func=mock_capture,
        fps_target=60,
    )
    pipeline.start()
    import time
    time.sleep(0.1)
    pipeline.stop()

    frame, count, active_zones = pipeline.get_latest_processed()
    assert count >= 0
    assert frame_count > 0
