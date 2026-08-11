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


def test_24h_chart_scale_lowered_to_0_05():
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
    js_content = response.text
    # Verify initial scale suggestedMax is lowered to 0.005 or dynamic minimum
    assert "suggestedMax: 0.005" in js_content or "suggestedMax: 0.01" in js_content, "24-hour chart scale suggestedMax should be set to small initial scale"
    assert "suggestedMax: 0.5" not in js_content, "24-hour chart scale suggestedMax should no longer be 0.5"
    # Verify dynamic scale adjustment logic adjusts strictly to maxVal without forcing large minimum floor
    assert "powerChart.options.scales.y.suggestedMax" in js_content, "Dynamic scale adjustment logic should be present"
    assert "maxVal > 0 ? maxVal * 1.15 : 0.005" in js_content, "Tight dynamic scaling formula should be present"



