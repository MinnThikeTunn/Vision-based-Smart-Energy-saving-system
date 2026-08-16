from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_weekly_trend_api_contract():
    """Verify /api/analytics/weekly returns 7-day trend with complete KPI metrics."""
    response = client.get("/api/analytics/weekly")
    assert response.status_code == 200
    data = response.json()
    assert "weekly_trend" in data
    trend = data["weekly_trend"]
    assert isinstance(trend, list)
    assert len(trend) == 7

    required_keys = {
        "date",
        "total_kwh_actual",
        "total_kwh_baseline",
        "total_kwh_saved",
        "savings_percentage",
        "total_cost_saved_usd",
        "total_co2_saved_kg",
    }
    for day in trend:
        assert required_keys.issubset(day.keys()), f"Day entry missing required keys: {day}"


def test_weekly_trend_modal_dom_elements():
    """Verify index.html contains weekly trend modal, line chart canvas, and summary elements."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    html = response.text

    # Verify modal wrapper and canvas
    assert 'id="weekly-trend-modal"' in html, "Missing #weekly-trend-modal in index.html"
    assert 'id="weeklyTrendChart"' in html, "Missing #weeklyTrendChart canvas in index.html"

    # Verify modal close action and title
    assert "toggleWeeklyModal(false)" in html or "toggleWeeklyModal()" in html
    assert "7-Day Energy & Savings Trend" in html or "7-Day Trend" in html

    # Verify summary stat badges inside modal
    assert 'id="weekly-modal-saved-kwh"' in html
    assert 'id="weekly-modal-saved-cost"' in html
    assert 'id="weekly-modal-efficiency"' in html


def test_weekly_trend_js_line_chart_logic():
    """Verify app.js creates Chart.js line chart for weekly trend without alert()."""
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
    js_content = response.text

    # Ensure alert() is removed from toggleWeeklyModal
    assert "alert(summaryText)" not in js_content, "alert() should be removed from toggleWeeklyModal"

    # Ensure weeklyTrendChart or initWeeklyChart is implemented
    assert "weeklyTrendChart" in js_content or "renderWeeklyTrendChart" in js_content
    assert "type: 'line'" in js_content or 'type: "line"' in js_content
