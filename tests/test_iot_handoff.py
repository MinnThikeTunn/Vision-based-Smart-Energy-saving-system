from fastapi.testclient import TestClient
from app.main import app
from app.analytics.report_generator import IoTHandoffReportGenerator

client = TestClient(app)


def test_iot_handoff_report_generator():
    handoff_text = IoTHandoffReportGenerator.generate_iot_handoff_report()
    assert "IOT HARDWARE INTEGRATION HANDOFF REPORT" in handoff_text
    assert "BaseDeviceController" in handoff_text
    assert "The Judgment & Critique" in handoff_text
    assert "ESP32 Boot Pin Traps" in handoff_text
    assert "MQTT Protocol Spec" in handoff_text
    assert "Hardware Safety, Fail-Safe, & Edge Resiliency Rules" in handoff_text


def test_download_iot_handoff_report_endpoint():
    response = client.get("/api/reports/iot_handoff")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")

    md_response = client.get("/api/reports/iot_handoff?format=md")
    assert md_response.status_code == 200
    assert md_response.headers["content-type"].startswith("text/markdown")
    assert "IOT HARDWARE INTEGRATION HANDOFF REPORT" in md_response.text
    assert "The Judgment & Critique" in md_response.text



def test_download_iot_handoff_report_pdf_endpoint():
    response = client.get("/api/reports/iot_handoff/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].endswith('.pdf"')
    assert len(response.content) > 500
    assert response.content.startswith(b"%PDF")

