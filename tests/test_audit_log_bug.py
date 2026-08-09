import json
from app.main import app
from app.api.ws_router import build_telemetry_payload
from fastapi.testclient import TestClient

client = TestClient(app)

def test_telemetry_payload_contains_event_logs():
    """Verify backend websocket telemetry includes event_logs list."""
    payload = build_telemetry_payload()
    assert "event_logs" in payload, "WebSocket telemetry payload must include 'event_logs'"
    assert isinstance(payload["event_logs"], list)

def test_audit_logs_api_endpoint_exists():
    """Verify audit logs REST endpoint returns audit logs list."""
    response = client.get("/api/config/audit_logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_frontend_js_handles_event_logs():
    """Verify frontend app.js contains logic to handle event_logs and update event-log-rows."""
    with open("app/static/js/app.js", "r", encoding="utf-8") as f:
        app_js_content = f.read()

    # The frontend app.js MUST call render/update function for event_logs
    assert "event_logs" in app_js_content or "renderEventLogs" in app_js_content or "event-log-rows" in app_js_content, \
        "app.js must handle rendering data.event_logs to the UI"

def test_frontend_index_html_has_audit_badge():
    """Verify index.html contains audit-log-badge and event-log-rows."""
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    assert 'id="audit-log-badge"' in html_content
    assert 'id="event-log-rows"' in html_content
