import time
from typing import Dict, Any


class MetricsRegistry:
    """
    Native Prometheus & Telemetry Metrics Registry.
    Generates OpenMetrics standard text format for scraping on /metrics.
    """

    def __init__(self) -> None:
        self.fps: float = 30.0
        self.occupant_count: int = 0
        self.room_status: str = "EMPTY"
        self.active_devices: int = 0
        self.current_power_watts: float = 0.0
        self.cumulative_kwh_saved: float = 0.0
        self.cumulative_cost_saved_usd: float = 0.0
        self.co2_saved_kg: float = 0.0

    def update_telemetry(
        self,
        fps: float,
        occupant_count: int,
        room_status: str,
        device_states: Dict[str, str],
        energy_metrics: Dict[str, Any],
    ) -> None:
        self.fps = fps
        self.occupant_count = occupant_count
        self.room_status = room_status
        self.active_devices = sum(1 for state in device_states.values() if state.upper() in ["ON", "DIM"])
        self.current_power_watts = energy_metrics.get("current_power_watts", 0.0)
        self.cumulative_kwh_saved = energy_metrics.get("saved_kwh", 0.0)
        self.cumulative_cost_saved_usd = energy_metrics.get("saved_cost_usd", 0.0)
        self.co2_saved_kg = energy_metrics.get("saved_co2_kg", 0.0)

    def generate_prometheus_metrics(self) -> str:
        lines = [
            "# HELP vision_fps Current video inference frame rate per second",
            "# TYPE vision_fps gauge",
            f"vision_fps {self.fps:.1f}",
            "",
            "# HELP occupancy_person_count Live detected occupant count in camera view",
            "# TYPE occupancy_person_count gauge",
            f"occupancy_person_count {self.occupant_count}",
            "",
            "# HELP room_occupied_status Numeric room occupancy status (1 = Occupied, 0 = Empty)",
            "# TYPE room_occupied_status gauge",
            f"room_occupied_status {1 if self.room_status == 'OCCUPIED' else 0}",
            "",
            "# HELP active_devices_count Number of currently active appliances (ON/DIM)",
            "# TYPE active_devices_count gauge",
            f"active_devices_count {self.active_devices}",
            "",
            "# HELP current_power_consumption_watts Total real-time power draw across active appliances",
            "# TYPE current_power_consumption_watts gauge",
            f"current_power_consumption_watts {self.current_power_watts:.1f}",
            "",
            "# HELP energy_kwh_saved_total Cumulative energy saved in kilowatt-hours vs baseline",
            "# TYPE energy_kwh_saved_total counter",
            f"energy_kwh_saved_total {self.cumulative_kwh_saved:.4f}",
            "",
            "# HELP energy_cost_saved_usd_total Cumulative energy cost saved in USD vs baseline",
            "# TYPE energy_cost_saved_usd_total counter",
            f"energy_cost_saved_usd_total {self.cumulative_cost_saved_usd:.4f}",
            "",
            "# HELP energy_co2_saved_kg_total Cumulative CO2 emissions prevented in kg",
            "# TYPE energy_co2_saved_kg_total counter",
            f"energy_co2_saved_kg_total {self.co2_saved_kg:.4f}",
        ]
        return "\n".join(lines) + "\n"


_global_metrics = MetricsRegistry()


def get_metrics_registry() -> MetricsRegistry:
    return _global_metrics
