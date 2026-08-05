import time
from typing import Dict, Any, List


class EnergyCalculator:
    """
    Real-time ROI & Energy Analytics Engine.
    
    Calculates cumulative energy savings (kWh), cost savings ($),
    and CO2 emission reductions (kg CO2e) against an Always-ON baseline.
    """

    def __init__(
        self,
        device_wattages: Dict[str, float] | None = None,
        electricity_rate_kwh: float = 0.15,
        co2_per_kwh_kg: float = 0.42,
    ) -> None:
        self.device_wattages: Dict[str, float] = device_wattages or {
            "light": 40.0,
            "fan": 65.0,
            "ac": 1200.0,
        }
        self.electricity_rate_kwh: float = electricity_rate_kwh
        self.co2_per_kwh_kg: float = co2_per_kwh_kg

        self._last_update_time: float = time.time()
        self.cumulative_kwh_baseline: float = 0.0
        self.cumulative_kwh_actual: float = 0.0

    def update(self, device_states: Dict[str, str], device_telemetry: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Any]:
        """
        Update energy accumulation over elapsed time step.
        """
        now = time.time()
        elapsed_hours = (now - self._last_update_time) / 3600.0
        self._last_update_time = now

        baseline_power_watts = sum(self.device_wattages.values())
        actual_power_watts = 0.0

        for dev_id, rated_w in self.device_wattages.items():
            state = device_states.get(dev_id, "OFF").upper()
            power_pct = 0.0
            if device_telemetry and dev_id in device_telemetry:
                power_pct = device_telemetry[dev_id].get("power_pct", 0.0) / 100.0
            else:
                power_pct = 1.0 if state == "ON" else (0.3 if state == "DIM" else 0.0)

            actual_power_watts += rated_w * power_pct

        self.cumulative_kwh_baseline += (baseline_power_watts / 1000.0) * elapsed_hours
        self.cumulative_kwh_actual += (actual_power_watts / 1000.0) * elapsed_hours

        saved_kwh = max(0.0, self.cumulative_kwh_baseline - self.cumulative_kwh_actual)
        saved_cost = saved_kwh * self.electricity_rate_kwh
        saved_co2_kg = saved_kwh * self.co2_per_kwh_kg

        efficiency_pct = (
            (saved_kwh / self.cumulative_kwh_baseline * 100.0)
            if self.cumulative_kwh_baseline > 0
            else 0.0
        )

        return {
            "current_power_watts": round(actual_power_watts, 1),
            "baseline_power_watts": round(baseline_power_watts, 1),
            "cumulative_kwh_baseline": round(self.cumulative_kwh_baseline, 4),
            "cumulative_kwh_actual": round(self.cumulative_kwh_actual, 4),
            "saved_kwh": round(saved_kwh, 4),
            "saved_cost_usd": round(saved_cost, 4),
            "saved_co2_kg": round(saved_co2_kg, 4),
            "energy_efficiency_pct": round(efficiency_pct, 1),
        }
