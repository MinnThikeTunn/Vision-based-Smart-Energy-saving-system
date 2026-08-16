import datetime
from app.analytics.energy_calculator import EnergyCalculator
from app.config.schema import SystemConfiguration


def test_tou_tariff_disabled_defaults_to_flat_rate():
    calc = EnergyCalculator(
        device_wattages={"lamp": 50.0},
        electricity_rate_kwh=0.15,
        tou_config={"enabled": False, "off_peak_rate_kwh": 0.10, "tiers": []},
    )
    dt = datetime.datetime(2026, 8, 17, 15, 0, 0)  # Monday 3 PM
    rate, tier = calc.get_current_tariff(dt)
    assert rate == 0.15
    assert tier == "FLAT"


def test_tou_tariff_peak_tier_activation():
    calc = EnergyCalculator(
        device_wattages={"lamp": 50.0},
        electricity_rate_kwh=0.15,
        tou_config={
            "enabled": True,
            "off_peak_rate_kwh": 0.10,
            "tiers": [
                {"name": "PEAK", "rate_kwh": 0.28, "start_hour": 14, "end_hour": 19, "days": [0, 1, 2, 3, 4]},
                {"name": "MID_PEAK", "rate_kwh": 0.18, "start_hour": 8, "end_hour": 14, "days": [0, 1, 2, 3, 4]},
            ],
        },
    )
    # Monday 15:00 (3 PM) -> PEAK ($0.28)
    dt_peak = datetime.datetime(2026, 8, 17, 15, 0, 0)
    rate, tier = calc.get_current_tariff(dt_peak)
    assert rate == 0.28
    assert tier == "PEAK"

    # Monday 10:00 (10 AM) -> MID_PEAK ($0.18)
    dt_mid = datetime.datetime(2026, 8, 17, 10, 0, 0)
    rate, tier = calc.get_current_tariff(dt_mid)
    assert rate == 0.18
    assert tier == "MID_PEAK"

    # Monday 22:00 (10 PM) -> OFF_PEAK ($0.10)
    dt_off = datetime.datetime(2026, 8, 17, 22, 0, 0)
    rate, tier = calc.get_current_tariff(dt_off)
    assert rate == 0.10
    assert tier == "OFF_PEAK"

    # Sunday 15:00 (Weekend) -> OFF_PEAK ($0.10)
    dt_weekend = datetime.datetime(2026, 8, 16, 15, 0, 0)
    rate, tier = calc.get_current_tariff(dt_weekend)
    assert rate == 0.10
    assert tier == "OFF_PEAK"


def test_tou_tariff_cost_calculation_in_update():
    calc = EnergyCalculator(
        device_wattages={"lamp": 1000.0},
        electricity_rate_kwh=0.15,
        edge_compute_watts=0.0,
        schedule_config={"enabled": False},
        tou_config={
            "enabled": True,
            "off_peak_rate_kwh": 0.10,
            "tiers": [
                {"name": "PEAK", "rate_kwh": 0.30, "start_hour": 14, "end_hour": 19, "days": [0, 1, 2, 3, 4]},
            ],
        },
    )
    t0 = datetime.datetime(2026, 8, 17, 15, 0, 0)
    calc._last_update_time = t0.timestamp()

    # 1 hour later, device OFF -> saved 1.0 kWh during PEAK ($0.30/kWh)
    t1 = datetime.datetime(2026, 8, 17, 16, 0, 0)
    result = calc.update(device_states={"lamp": "OFF"}, now_datetime=t1)

    assert result["saved_kwh"] == 1.0
    assert result["tariff_tier"] == "PEAK"
    assert result["tariff_rate_kwh"] == 0.30
    assert result["saved_cost_usd"] == 0.30
