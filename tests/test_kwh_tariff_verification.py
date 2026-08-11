import pytest
from app.analytics.energy_calculator import EnergyCalculator

def test_one_kwh_equals_fifteen_cents():
    """Verify that 1.0 kWh cumulative saved energy translates to $0.15 at $0.15/kWh tariff rate."""
    calc = EnergyCalculator(
        electricity_rate_kwh=0.15,
        co2_per_kwh_kg=0.42,
        edge_compute_watts=0.0, # Zero out edge compute for exact 1 kWh test
    )

    # Manually set baseline to 1.0 kWh and actual to 0.0 kWh
    calc.cumulative_kwh_baseline = 1.0
    calc.cumulative_kwh_actual = 0.0

    metrics = calc.update(device_states={"light": "OFF"})

    assert metrics["saved_kwh"] == 1.0
    assert metrics["saved_cost_usd"] == 0.15
    assert metrics["saved_co2_kg"] == 0.42

    print("\n[VERIFIED] 1.0 kWh saved = $" + str(metrics["saved_cost_usd"]) + " (at $0.15/kWh rate)")
