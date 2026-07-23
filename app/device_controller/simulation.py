from datetime import datetime
from typing import Any
import uuid
from app.device_controller.base import BaseDeviceController


class SimulationController(BaseDeviceController):
    def __init__(self) -> None:
        self._states: dict[str, str] = {
            "light": "OFF",
            "fan": "OFF",
            "ac": "OFF",
        }
        self._event_logs: list[dict[str, Any]] = []

    def set_device_state(self, device_id: str, state: str, reason: str = "") -> bool:
        device_key = device_id.lower()
        target_state = state.upper()
        if device_key not in self._states:
            self._states[device_key] = "OFF"

        previous_state = self._states.get(device_key, "OFF")
        if previous_state == target_state:
            return False  # Prevent redundant log spam

        self._states[device_key] = target_state

        event_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "device_id": device_key,
            "action": target_state,
            "reason": reason or "Automated rule trigger",
            "mode": "Simulation",
        }
        self._event_logs.insert(0, event_entry)
        if len(self._event_logs) > 100:
            self._event_logs.pop()

        return True

    def get_device_states(self) -> dict[str, str]:
        return self._states.copy()

    def get_event_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._event_logs[:limit]
