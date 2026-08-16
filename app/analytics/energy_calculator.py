import datetime
import time
from typing import Dict, Any, List


class EnergyCalculator:
    """
    Real-time ROI & Energy Analytics Engine (Version 3.0).
    
    Calculates net cumulative energy savings (kWh), cost savings ($),
    and CO2 emission reductions (kg CO2e) subtracting edge compute overhead
    and applying business operating schedule masks.
    """

    def __init__(
        self,
        device_wattages: Dict[str, float] | None = None,
        electricity_rate_kwh: float = 0.15,
        co2_per_kwh_kg: float = 0.42,
        edge_compute_watts: float = 30.0,
        schedule_config: Dict[str, Any] | None = None,
        tou_config: Dict[str, Any] | None = None,
    ) -> None:
        self.device_wattages: Dict[str, float] = device_wattages or {
            "light": 40.0,
            "fan": 65.0,
            "ac": 1200.0,
        }
        self.electricity_rate_kwh: float = electricity_rate_kwh
        self.co2_per_kwh_kg: float = co2_per_kwh_kg
        self.edge_compute_watts: float = edge_compute_watts
        self.schedule_config: Dict[str, Any] = schedule_config or {
            "enabled": True,
            "operating_days": [0, 1, 2, 3, 4, 5, 6],
            "start_hour": 0,
            "end_hour": 24,
        }
        self.tou_config: Dict[str, Any] = tou_config or {
            "enabled": False,
            "off_peak_rate_kwh": 0.10,
            "tiers": [
                {"name": "PEAK", "rate_kwh": 0.28, "start_hour": 14, "end_hour": 19, "days": [0, 1, 2, 3, 4]},
                {"name": "MID_PEAK", "rate_kwh": 0.18, "start_hour": 8, "end_hour": 14, "days": [0, 1, 2, 3, 4]},
            ],
        }

        self._last_update_time: float = time.time()
        self.cumulative_kwh_baseline: float = 0.0
        self.cumulative_kwh_actual: float = 0.0
        self.cumulative_saved_cost: float = 0.0

    def _is_within_schedule(self, dt: datetime.datetime) -> bool:
        """Check if datetime falls within configured business operating schedule."""
        if not self.schedule_config.get("enabled", True):
            return True
        
        day_of_week = dt.weekday()  # 0=Monday..6=Sunday
        operating_days = self.schedule_config.get("operating_days", [0, 1, 2, 3, 4])
        if day_of_week not in operating_days:
            return False

        hour = dt.hour
        start_hour = self.schedule_config.get("start_hour", 8)
        end_hour = self.schedule_config.get("end_hour", 19)
        return start_hour <= hour <= end_hour

    def get_current_tariff(self, dt: datetime.datetime) -> tuple[float, str]:
        """
        Determine active electricity rate and tariff tier for given datetime.
        Returns: (rate_kwh, tier_name)
        """
        if not self.tou_config or not self.tou_config.get("enabled", False):
            return self.electricity_rate_kwh, "FLAT"

        day_of_week = dt.weekday()
        hour = dt.hour

        tiers = self.tou_config.get("tiers", [])
        for tier in tiers:
            tier_dict = tier if isinstance(tier, dict) else tier.model_dump() if hasattr(tier, "model_dump") else tier.__dict__
            days = tier_dict.get("days", [0, 1, 2, 3, 4])
            start_h = tier_dict.get("start_hour", 0)
            end_h = tier_dict.get("end_hour", 24)
            if day_of_week in days and start_h <= hour < end_h:
                return float(tier_dict.get("rate_kwh", self.electricity_rate_kwh)), str(tier_dict.get("name", "TIER"))

        off_peak_rate = float(self.tou_config.get("off_peak_rate_kwh", 0.10))
        return off_peak_rate, "OFF_PEAK"

    def update(
        self,
        device_states: Dict[str, str],
        device_telemetry: Dict[str, Dict[str, Any]] | None = None,
        now_datetime: datetime.datetime | None = None,
    ) -> Dict[str, Any]:
        """
        Update energy accumulation over elapsed time step.
        """
        current_dt = now_datetime or datetime.datetime.now()
        now_ts = current_dt.timestamp() if now_datetime else time.time()
        elapsed_hours = max(0.0, (now_ts - self._last_update_time) / 3600.0)
        self._last_update_time = now_ts

        is_active_schedule = self._is_within_schedule(current_dt)
        current_rate, current_tier = self.get_current_tariff(current_dt)

        raw_baseline = sum(self.device_wattages.values()) if self.device_wattages else 1305.0
        baseline_power_watts = raw_baseline if raw_baseline > 0 else 1305.0
        actual_power_watts = 0.0

        for dev_id, rated_w in self.device_wattages.items():
            state = device_states.get(dev_id, "OFF").upper()
            power_pct = 0.0
            if device_telemetry and dev_id in device_telemetry:
                power_pct = device_telemetry[dev_id].get("power_pct", 0.0) / 100.0
            else:
                power_pct = 1.0 if state == "ON" else (0.3 if state == "DIM" else 0.0)

            actual_power_watts += rated_w * power_pct

        # Baseline energy accumulates strictly when operating schedule is active
        delta_baseline_kwh = (baseline_power_watts / 1000.0) * elapsed_hours if is_active_schedule else 0.0
        self.cumulative_kwh_baseline += delta_baseline_kwh

        total_actual_watts = actual_power_watts + self.edge_compute_watts
        delta_actual_kwh = (total_actual_watts / 1000.0) * elapsed_hours
        self.cumulative_kwh_actual += delta_actual_kwh

        active_baseline_watts = baseline_power_watts if is_active_schedule else baseline_power_watts

        # Net saved kWh formula (subtracting edge compute overhead)
        saved_kwh = max(0.0, self.cumulative_kwh_baseline - self.cumulative_kwh_actual)
        saved_cost = saved_kwh * current_rate
        saved_co2_kg = saved_kwh * self.co2_per_kwh_kg

        efficiency_pct = (
            (saved_kwh / self.cumulative_kwh_baseline * 100.0)
            if self.cumulative_kwh_baseline > 0
            else 0.0
        )

        return {
            "current_power_watts": round(total_actual_watts, 1),
            "device_power_watts": round(actual_power_watts, 1),
            "edge_compute_watts": round(self.edge_compute_watts, 1),
            "baseline_power_watts": round(active_baseline_watts, 1),
            "rated_baseline_watts": round(baseline_power_watts, 1),
            "cumulative_kwh_baseline": round(self.cumulative_kwh_baseline, 4),
            "cumulative_kwh_actual": round(self.cumulative_kwh_actual, 4),
            "saved_kwh": round(saved_kwh, 4),
            "saved_cost_usd": round(saved_cost, 4),
            "saved_co2_kg": round(saved_co2_kg, 4),
            "energy_efficiency_pct": round(efficiency_pct, 1),
            "schedule_active": is_active_schedule,
            "tariff_tier": current_tier,
            "tariff_rate_kwh": current_rate,
        }



