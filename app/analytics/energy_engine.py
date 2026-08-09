from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from app.analytics.energy_logger import EnergyLogger


class EnergyAnalyticsEngine:
    """
    Analytics Aggregation Engine.
    
    Aggregates raw 5-minute interval energy snapshots into 24-hour hourly breakdowns,
    consolidated daily metrics, and 7-day trend summaries.
    """

    def __init__(self, logger: Optional[EnergyLogger] = None) -> None:
        self.logger = logger or EnergyLogger()

    def get_hourly_summary(
        self,
        target_date: Optional[date] = None,
        logs: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        d = target_date or datetime.now().date()
        raw_entries = logs if logs is not None else self.logger.load_logs_for_date(d)

        # Bucket entries by hour (0 to 23)
        hourly_buckets: Dict[int, List[Dict[str, Any]]] = {h: [] for h in range(24)}
        for entry in raw_entries:
            h = entry.get("hour", 0)
            if 0 <= h < 24:
                hourly_buckets[h].append(entry)

        summary: List[Dict[str, Any]] = []

        for hour in range(24):
            entries = hourly_buckets[hour]
            if not entries:
                summary.append({
                    "hour": hour,
                    "kwh_actual": 0.0,
                    "kwh_baseline": 0.0,
                    "kwh_saved": 0.0,
                    "avg_power_watts": 0.0,
                    "peak_power_watts": 0.0,
                    "schedule_active": 8 <= hour < 19,  # default schedule mask hint
                    "active_hours": 0.0,
                    "occupancy_events": 0,
                    "device_usage_hours": {},
                })
                continue

            kwh_actual = sum(e.get("delta_kwh_actual", 0.0) for e in entries)
            kwh_baseline = sum(e.get("delta_kwh_baseline", 0.0) for e in entries)
            kwh_saved = max(0.0, kwh_baseline - kwh_actual)

            power_draws = [e.get("current_power_watts", 0.0) for e in entries]
            avg_power = sum(power_draws) / len(power_draws) if power_draws else 0.0
            peak_power = max(power_draws) if power_draws else 0.0

            schedule_active = any(e.get("schedule_active", True) for e in entries)
            max_occupants = max(e.get("occupant_count", 0) for e in entries)

            # Calculate device usage hours in this 60-min window (each snapshot = 5 mins = 1/12 hour)
            interval_hours = (self.logger.log_interval_sec / 3600.0) if self.logger else (5.0 / 60.0)
            device_counts: Dict[str, float] = {}
            for e in entries:
                active_devs = e.get("active_devices", [])
                if isinstance(active_devs, str):
                    active_devs = [d for d in active_devs.split(",") if d]
                for dev in active_devs:
                    device_counts[dev] = device_counts.get(dev, 0.0) + interval_hours

            active_fraction = round(len(entries) * interval_hours, 2)

            summary.append({
                "hour": hour,
                "kwh_actual": round(kwh_actual, 4),
                "kwh_baseline": round(kwh_baseline, 4),
                "kwh_saved": round(kwh_saved, 4),
                "avg_power_watts": round(avg_power, 1),
                "peak_power_watts": round(peak_power, 1),
                "schedule_active": schedule_active,
                "active_hours": min(1.0, active_fraction),
                "occupancy_events": max_occupants,
                "device_usage_hours": {dev: round(hrs, 2) for dev, hrs in device_counts.items()},
            })

        return summary

    def get_daily_summary(
        self,
        target_date: Optional[date] = None,
        logs: Optional[List[Dict[str, Any]]] = None,
        electricity_rate_kwh: float = 0.15,
        co2_per_kwh_kg: float = 0.42,
    ) -> Dict[str, Any]:
        d = target_date or datetime.now().date()
        date_str = d.strftime("%Y-%m-%d")
        hourly = self.get_hourly_summary(target_date=d, logs=logs)

        tot_actual = sum(h["kwh_actual"] for h in hourly)
        tot_baseline = sum(h["kwh_baseline"] for h in hourly)
        tot_saved = max(0.0, tot_baseline - tot_actual)

        cost_saved = tot_saved * electricity_rate_kwh
        co2_saved = tot_saved * co2_per_kwh_kg

        savings_pct = (tot_saved / tot_baseline * 100.0) if tot_baseline > 0 else 0.0

        peak_power = 0.0
        peak_hour = 0
        all_powers = []

        for h in hourly:
            all_powers.append(h["peak_power_watts"])
            if h["peak_power_watts"] > peak_power:
                peak_power = h["peak_power_watts"]
                peak_hour = h["hour"]

        avg_power = sum(all_powers) / len(all_powers) if all_powers else 0.0

        # Aggregate total device usage hours across 24 hours
        total_device_hours: Dict[str, float] = {}
        for h in hourly:
            for dev, hrs in h.get("device_usage_hours", {}).items():
                total_device_hours[dev] = round(total_device_hours.get(dev, 0.0) + hrs, 2)

        return {
            "date": date_str,
            "total_kwh_actual": round(tot_actual, 4),
            "total_kwh_baseline": round(tot_baseline, 4),
            "total_kwh_saved": round(tot_saved, 4),
            "savings_percentage": round(savings_pct, 1),
            "total_cost_saved_usd": round(cost_saved, 4),
            "total_co2_saved_kg": round(co2_saved, 4),
            "peak_power_watts": round(peak_power, 1),
            "peak_hour": peak_hour,
            "avg_power_watts": round(avg_power, 1),
            "device_usage_hours": total_device_hours,
        }

    def get_weekly_summary(
        self,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        d_end = end_date or datetime.now().date()
        days_summary = []
        for i in range(6, -1, -1):
            day = d_end - timedelta(days=i)
            daily = self.get_daily_summary(target_date=day)
            days_summary.append(daily)
        return days_summary
