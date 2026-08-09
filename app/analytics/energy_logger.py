import os
import csv
import time
from collections import deque
from datetime import datetime, date
from typing import Dict, Any, List, Optional


class EnergyLogger:
    """
    Time-Series Energy Logger.
    
    Logs 5-minute interval energy snapshots with in-memory rolling buffer (7 days = 2,016 entries)
    and automatic daily CSV persistence for 24-hour analytics.
    """

    def __init__(
        self,
        log_interval_sec: float = 300.0,
        log_dir: str = "data/logs",
        max_memory_entries: int = 2016,
    ) -> None:
        self.log_interval_sec: float = log_interval_sec
        self.log_dir: str = log_dir
        self.energy_log: deque[Dict[str, Any]] = deque(maxlen=max_memory_entries)
        self.last_log_time: float = time.time()
        self.last_cumulative_baseline: float = 0.0
        self.last_cumulative_actual: float = 0.0

        os.makedirs(self.log_dir, exist_ok=True)

    def _get_csv_filename(self, target_date: Optional[date] = None) -> str:
        d = target_date or datetime.now().date()
        return os.path.join(self.log_dir, f"energy_{d.strftime('%Y-%m-%d')}.csv")

    def should_log(self, current_ts: Optional[float] = None) -> bool:
        ts = current_ts or time.time()
        return (ts - self.last_log_time) >= self.log_interval_sec

    def log_snapshot(
        self,
        energy_metrics: Dict[str, Any],
        device_states: Dict[str, str],
        occupant_count: int = 0,
        now_dt: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        dt = now_dt or datetime.now()
        current_ts = dt.timestamp() if now_dt else time.time()

        cumulative_baseline = energy_metrics.get("cumulative_kwh_baseline", 0.0)
        cumulative_actual = energy_metrics.get("cumulative_kwh_actual", 0.0)

        delta_baseline = max(0.0, cumulative_baseline - self.last_cumulative_baseline)
        delta_actual = max(0.0, cumulative_actual - self.last_cumulative_actual)
        delta_saved = max(0.0, delta_baseline - delta_actual)

        self.last_cumulative_baseline = cumulative_baseline
        self.last_cumulative_actual = cumulative_actual
        self.last_log_time = current_ts

        active_devices = [
            dev for dev, state in device_states.items() if state.upper() in ("ON", "DIM")
        ]

        entry = {
            "timestamp": dt.isoformat(),
            "date": dt.strftime("%Y-%m-%d"),
            "hour": dt.hour,
            "delta_kwh_baseline": round(delta_baseline, 6),
            "delta_kwh_actual": round(delta_actual, 6),
            "delta_saved_kwh": round(delta_saved, 6),
            "saved_cost_usd": round(energy_metrics.get("saved_cost_usd", 0.0), 4),
            "saved_co2_kg": round(energy_metrics.get("saved_co2_kg", 0.0), 4),
            "current_power_watts": energy_metrics.get("current_power_watts", 0.0),
            "baseline_power_watts": energy_metrics.get("baseline_power_watts", 0.0),
            "active_devices": ",".join(active_devices),
            "occupant_count": occupant_count,
            "schedule_active": 1 if energy_metrics.get("schedule_active", True) else 0,
        }

        self.energy_log.append(entry)
        self._persist_to_csv(entry, dt.date())
        return entry

    def _persist_to_csv(self, entry: Dict[str, Any], entry_date: date) -> None:
        filepath = self._get_csv_filename(entry_date)
        file_exists = os.path.exists(filepath)

        fieldnames = [
            "timestamp",
            "date",
            "hour",
            "delta_kwh_baseline",
            "delta_kwh_actual",
            "delta_saved_kwh",
            "saved_cost_usd",
            "saved_co2_kg",
            "current_power_watts",
            "baseline_power_watts",
            "active_devices",
            "occupant_count",
            "schedule_active",
        ]

        try:
            with open(filepath, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(entry)
        except Exception as e:
            print(f"Error persisting energy log to CSV: {e}")

    def load_logs_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        filepath = self._get_csv_filename(target_date)
        if not os.path.exists(filepath):
            return []

        entries = []
        try:
            with open(filepath, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parsed_row = {
                        "timestamp": row.get("timestamp", ""),
                        "date": row.get("date", target_date.strftime("%Y-%m-%d")),
                        "hour": int(row.get("hour", 0)),
                        "delta_kwh_baseline": float(row.get("delta_kwh_baseline", 0.0)),
                        "delta_kwh_actual": float(row.get("delta_kwh_actual", 0.0)),
                        "delta_saved_kwh": float(row.get("delta_saved_kwh", 0.0)),
                        "saved_cost_usd": float(row.get("saved_cost_usd", 0.0)),
                        "saved_co2_kg": float(row.get("saved_co2_kg", 0.0)),
                        "current_power_watts": float(row.get("current_power_watts", 0.0)),
                        "baseline_power_watts": float(row.get("baseline_power_watts", 0.0)),
                        "active_devices": [d for d in row.get("active_devices", "").split(",") if d],
                        "occupant_count": int(row.get("occupant_count", 0)),
                        "schedule_active": bool(int(row.get("schedule_active", 1))),
                    }
                    entries.append(parsed_row)
        except Exception as e:
            print(f"Error reading CSV energy log {filepath}: {e}")
        return entries

    def recover_todays_energy(self) -> Dict[str, float]:
        """Restore cumulative baseline & actual kWh from today's CSV on startup."""
        todays_entries = self.load_logs_for_date(datetime.now().date())
        tot_baseline = sum(e["delta_kwh_baseline"] for e in todays_entries)
        tot_actual = sum(e["delta_kwh_actual"] for e in todays_entries)
        self.last_cumulative_baseline = tot_baseline
        self.last_cumulative_actual = tot_actual
        return {
            "cumulative_kwh_baseline": tot_baseline,
            "cumulative_kwh_actual": tot_actual,
        }
