import os
import shutil
import tempfile
from datetime import date, datetime
import pytest

from app.analytics.energy_calculator import EnergyCalculator
from app.analytics.energy_logger import EnergyLogger
from app.analytics.energy_engine import EnergyAnalyticsEngine
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def temp_log_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


def test_energy_calculator_watt_fixes():
    ec = EnergyCalculator(
        device_wattages={"light": 50.0, "fan": 100.0},
        edge_compute_watts=30.0,
        schedule_config={"enabled": True, "operating_days": [0, 1, 2, 3, 4, 5, 6], "start_hour": 0, "end_hour": 24},
    )
    res = ec.update(device_states={"light": "ON", "fan": "OFF"})
    # current_power_watts should include 50W light + 30W edge compute = 80.0W
    assert res["current_power_watts"] == 80.0
    assert res["device_power_watts"] == 50.0
    assert res["edge_compute_watts"] == 30.0
    assert res["baseline_power_watts"] == 150.0


def test_energy_logger_snapshot_and_csv(temp_log_dir):
    logger = EnergyLogger(log_interval_sec=300.0, log_dir=temp_log_dir)
    metrics = {
        "cumulative_kwh_baseline": 1.5,
        "cumulative_kwh_actual": 0.5,
        "saved_kwh": 1.0,
        "saved_cost_usd": 0.15,
        "saved_co2_kg": 0.42,
        "current_power_watts": 80.0,
        "baseline_power_watts": 150.0,
        "schedule_active": True,
    }
    device_states = {"light": "ON", "fan": "OFF"}
    now = datetime(2026, 8, 10, 14, 15, 0)

    entry = logger.log_snapshot(metrics, device_states, occupant_count=2, now_dt=now)
    assert entry["hour"] == 14
    assert entry["delta_kwh_baseline"] == 1.5
    assert entry["delta_kwh_actual"] == 0.5

    logs = logger.load_logs_for_date(now.date())
    assert len(logs) == 1
    assert logs[0]["delta_kwh_baseline"] == 1.5
    assert logs[0]["delta_kwh_actual"] == 0.5
    assert logs[0]["occupant_count"] == 2
    assert "light" in logs[0]["active_devices"]


def test_analytics_engine_hourly_and_daily(temp_log_dir):
    logger = EnergyLogger(log_interval_sec=300.0, log_dir=temp_log_dir)
    engine = EnergyAnalyticsEngine(logger=logger)

    target_d = date(2026, 8, 10)
    # Log 2 snapshots in hour 14
    logger.log_snapshot(
        {"cumulative_kwh_baseline": 1.0, "cumulative_kwh_actual": 0.4, "current_power_watts": 100.0, "schedule_active": True},
        device_states={"light": "ON"},
        occupant_count=1,
        now_dt=datetime(2026, 8, 10, 14, 5, 0),
    )
    logger.log_snapshot(
        {"cumulative_kwh_baseline": 2.0, "cumulative_kwh_actual": 0.8, "current_power_watts": 120.0, "schedule_active": True},
        device_states={"light": "ON", "fan": "ON"},
        occupant_count=3,
        now_dt=datetime(2026, 8, 10, 14, 10, 0),
    )

    hourly = engine.get_hourly_summary(target_date=target_d)
    assert len(hourly) == 24
    h14 = hourly[14]
    assert h14["kwh_baseline"] == 2.0
    assert h14["kwh_actual"] == 0.8
    assert h14["peak_power_watts"] == 120.0
    assert h14["avg_power_watts"] == 110.0
    assert h14["occupancy_events"] == 3

    daily = engine.get_daily_summary(target_date=target_d)
    assert daily["total_kwh_baseline"] == 2.0
    assert daily["total_kwh_actual"] == 0.8
    assert daily["total_kwh_saved"] == 1.2
    assert daily["peak_power_watts"] == 120.0


def test_analytics_api_endpoints():
    client = TestClient(app)
    r1 = client.get("/api/analytics/hourly/today")
    assert r1.status_code == 200
    res1 = r1.json()
    assert "hourly_summary" in res1
    assert len(res1["hourly_summary"]) == 24

    r2 = client.get("/api/analytics/daily/today")
    assert r2.status_code == 200

    r3 = client.get("/api/analytics/export/csv")
    assert r3.status_code == 200
    assert "text/csv" in r3.headers["content-type"]
    assert "hour,kwh_actual" in r3.text
