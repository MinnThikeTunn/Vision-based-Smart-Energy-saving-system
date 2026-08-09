from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dashboard_index_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "Vision Smart Energy Saver" in response.text


def test_telemetry_stat_element_ids_exist():
    response = client.get("/")
    html = response.text

    expected_ids = [
        "stat-power-draw",
        "stat-baseline-power",
        "stat-saved-kwh",
        "stat-saved-co2",
        "stat-saved-cost",
        "stat-efficiency",
        "stat-forecast",
    ]
    for element_id in expected_ids:
        assert f'id="{element_id}"' in html, f"Missing {element_id} in index.html"

