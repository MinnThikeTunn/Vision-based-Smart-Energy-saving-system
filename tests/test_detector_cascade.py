from app.detector.person_detector import (
    BaseDetector,
    DummyDetector,
    YOLOPersonDetector,
    ONNXPersonDetector,
    create_detector,
)


def test_create_detector_explicit_dummy():
    det = create_detector(backend="dummy")
    assert isinstance(det, DummyDetector)


def test_create_detector_fallback_nonexistent():
    # If a non-existent model is given, it safely falls back to DummyDetector
    det = create_detector(model_name="nonexistent_model_12345.pt", backend="auto")
    assert isinstance(det, DummyDetector)


def test_create_detector_auto_cascade():
    det = create_detector(model_name="yolov8n.pt", backend="auto")
    assert isinstance(det, BaseDetector)


def test_onnx_person_detector_subclass():
    assert issubclass(ONNXPersonDetector, YOLOPersonDetector)
