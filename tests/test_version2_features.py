from app.analytics.energy_calculator import EnergyCalculator
from app.analytics.occupancy_forecast import OccupancyForecaster
from app.analytics.report_generator import FacilitiesReportGenerator
from app.detector.tracker import CentroidTracker
from app.telemetry.metrics import get_metrics_registry


def test_energy_calculator():
    calc = EnergyCalculator(device_wattages={"light": 40.0, "fan": 65.0, "ac": 1200.0}, edge_compute_watts=0.0)
    metrics = calc.update(device_states={"light": "OFF", "fan": "OFF", "ac": "OFF"})
    assert "saved_kwh" in metrics
    assert "saved_cost_usd" in metrics
    assert "current_power_watts" in metrics
    assert metrics["current_power_watts"] == 0.0


def test_centroid_tracker():
    tracker = CentroidTracker()
    boxes = [[10.0, 10.0, 50.0, 100.0]]
    tracked = tracker.update(boxes)
    assert len(tracked) == 1
    first_id = list(tracked.keys())[0]
    assert first_id == 1


def test_occupancy_forecaster():
    forecaster = OccupancyForecaster()
    result = forecaster.predict_next_hour()
    assert "target_hour" in result
    assert "predicted_occupancy_probability" in result


def test_facilities_report_generator():
    report_csv = FacilitiesReportGenerator.generate_csv_report(
        energy_metrics={"saved_kwh": 10.5, "saved_cost_usd": 1.57},
        device_states={"light": "OFF", "fan": "OFF", "ac": "OFF"},
        event_logs=[],
    )
    assert "VISION-BASED SMART ENERGY SAVING SYSTEM" in report_csv
    assert "saved_kwh" in report_csv or "10.5" in report_csv


def test_prometheus_metrics():
    registry = get_metrics_registry()
    metrics_text = registry.generate_prometheus_metrics()
    assert b"vision_fps" in metrics_text
    assert b"occupancy_person_count" in metrics_text



