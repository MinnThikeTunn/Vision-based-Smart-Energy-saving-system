import pytest
from app.api.ws_router import build_telemetry_payload, _energy_calculator
from app.analytics.energy_calculator import EnergyCalculator
from app.analytics.occupancy_forecast import OccupancyForecaster

def test_forecast_payload_and_ui_element_ids():
    """Verify forecast returns all required fields and app.js targets correct element IDs."""
    forecaster = OccupancyForecaster()
    forecast = forecaster.predict_next_hour()

    assert "predicted_occupancy_probability" in forecast
    assert "prewarm_hvac_recommended" in forecast
    assert "reason" in forecast

    with open("app/static/js/app.js", "r", encoding="utf-8") as f:
        app_js = f.read()

    # app.js updateForecast MUST update forecast-prob, forecast-status, and forecast-reason
    assert "forecast-prob" in app_js, "app.js must update #forecast-prob"
    assert "forecast-status" in app_js, "app.js must update #forecast-status"
    assert "forecast-reason" in app_js, "app.js must update #forecast-reason"


def test_energy_metrics_baseline_and_savings_calculation():
    """Verify baseline power is non-zero and energy metrics calculate savings."""
    calc = EnergyCalculator()
    # Update energy metrics with devices turned OFF (room empty or appliances off)
    metrics = calc.update(device_states={"light": "OFF", "fan": "OFF", "ac": "OFF"})

    assert metrics["baseline_power_watts"] > 0, "Baseline power must be non-zero"
    assert metrics["current_power_watts"] < metrics["rated_baseline_watts"]
    
    # Simulate 10 seconds of elapsed time
    calc._last_update_time -= 10.0
    metrics_after = calc.update(device_states={"light": "OFF", "fan": "OFF", "ac": "OFF"})
    
    assert metrics_after["saved_kwh"] > 0.0, "Saved kWh must be positive when devices are OFF"
    assert metrics_after["saved_cost_usd"] > 0.0, "Saved cost USD must be positive"
    assert metrics_after["energy_efficiency_pct"] > 0.0, "Efficiency percentage must be positive"
