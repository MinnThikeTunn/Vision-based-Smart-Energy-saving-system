import datetime
import time
from app.analytics.energy_calculator import EnergyCalculator
from app.config.schema import AnalyticsConfig, OperatingScheduleConfig, SystemConfiguration
from app.config.loader import load_settings


def test_energy_calculator_edge_compute_overhead_subtraction():
    """Verify that EnergyCalculator subtracts edge compute power overhead from saved kWh."""
    calculator = EnergyCalculator(
        device_wattages={"light": 40.0, "fan": 65.0, "ac": 1200.0},
        electricity_rate_kwh=0.15,
        co2_per_kwh_kg=0.42,
        edge_compute_watts=30.0,
    )

    monday_time = datetime.datetime(2026, 8, 10, 10, 0, 0)  # Monday 10 AM
    calculator._last_update_time = monday_time.timestamp() - 3600.0

    # Devices remain OFF for 1 hour
    # Baseline power = 1305.0 W (1.305 kW)
    # Actual device power = 0.0 W
    # Edge compute overhead = 30.0 W (0.030 kW)
    # Baseline kWh = 1.305 kWh
    # Actual total kWh = (0.0 + 30.0) / 1000 * 1 = 0.030 kWh
    # Net saved kWh = max(0, 1.305 - 0.030) = 1.275 kWh
    metrics = calculator.update(
        device_states={"light": "OFF", "fan": "OFF", "ac": "OFF"},
        now_datetime=monday_time,
    )

    assert metrics["edge_compute_watts"] == 30.0
    assert metrics["cumulative_kwh_baseline"] == 1.305
    assert metrics["cumulative_kwh_actual"] == 0.03
    assert metrics["saved_kwh"] == 1.275
    assert metrics["saved_cost_usd"] == round(1.275 * 0.15, 4)



def test_energy_calculator_operating_schedule_mask():
    """Verify that baseline energy accumulation occurs strictly within active operating schedule hours."""
    schedule_cfg = {
        "enabled": True,
        "operating_days": [0, 1, 2, 3, 4],  # Mon-Fri
        "start_hour": 8,
        "end_hour": 19,
    }
    calculator = EnergyCalculator(
        device_wattages={"light": 40.0},
        electricity_rate_kwh=0.15,
        schedule_config=schedule_cfg,
    )

    # Simulated outside operating schedule (e.g. Sunday at 2 AM)
    outside_time = datetime.datetime(2026, 8, 9, 2, 0, 0)  # Sunday
    calculator._last_update_time = outside_time.timestamp() - 3600.0

    metrics_outside = calculator.update(
        device_states={"light": "OFF"},
        now_datetime=outside_time,
    )

    # Outside schedule -> Baseline power should NOT accumulate (remains 0.0 kWh)
    assert metrics_outside["cumulative_kwh_baseline"] == 0.0

    # Simulated inside operating schedule (e.g. Monday at 10 AM)
    inside_time = datetime.datetime(2026, 8, 10, 10, 0, 0)  # Monday
    calculator._last_update_time = inside_time.timestamp() - 3600.0

    metrics_inside = calculator.update(
        device_states={"light": "OFF"},
        now_datetime=inside_time,
    )

    # Inside schedule -> Baseline power accumulates 40W * 1 hr = 0.04 kWh
    assert metrics_inside["cumulative_kwh_baseline"] == 0.04


def test_analytics_config_schema_extension():
    """Verify that AnalyticsConfig and SystemConfiguration include edge_compute_watts and schedule parameters."""
    cfg = AnalyticsConfig()
    assert hasattr(cfg, "edge_compute_watts")
    assert cfg.edge_compute_watts == 30.0
    assert hasattr(cfg, "schedule")
    assert cfg.schedule.enabled is True
    assert cfg.schedule.operating_days == [0, 1, 2, 3, 4]
    assert cfg.schedule.start_hour == 8
    assert cfg.schedule.end_hour == 19
