from fastapi.testclient import TestClient
from app.main import app
from app.analytics.report_generator import IoTHandoffReportGenerator

client = TestClient(app)


def test_iot_handoff_report_generator():
    handoff_text = IoTHandoffReportGenerator.generate_iot_handoff_report()
    assert "IOT HARDWARE INTEGRATION HANDOFF REPORT" in handoff_text
    assert "BaseDeviceController" in handoff_text
    assert "MQTT / HTTP API Payload Schema" in handoff_text


def test_download_iot_handoff_report_endpoint():
    response = client.get("/api/reports/iot_handoff")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "IOT HARDWARE INTEGRATION HANDOFF REPORT" in response.text
