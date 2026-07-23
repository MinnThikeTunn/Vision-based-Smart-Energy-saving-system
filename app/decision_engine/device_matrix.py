from typing import Any
from app.decision_engine.state_machine import RoomState


class DeviceControlMatrix:
    def __init__(self, device_timeouts: dict[str, float]):
        """
        device_timeouts e.g.: {'light': 180, 'fan': 600, 'ac': 600}
        """
        self.device_timeouts = device_timeouts

    def evaluate(
        self,
        room_state: RoomState,
        empty_duration_sec: float,
        current_states: dict[str, str],
    ) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []

        for device_id, timeout in self.device_timeouts.items():
            current_state = current_states.get(device_id, "OFF").upper()

            if room_state == RoomState.OCCUPIED and current_state != "ON":
                actions.append(
                    {
                        "device_id": device_id,
                        "action": "TURN_ON",
                        "reason": "Occupant detected in room",
                    }
                )
            elif (
                room_state == RoomState.EMPTY
                and empty_duration_sec >= timeout
                and current_state != "OFF"
            ):
                actions.append(
                    {
                        "device_id": device_id,
                        "action": "TURN_OFF",
                        "reason": f"Room empty for {empty_duration_sec:.0f}s (timeout: {timeout:.0f}s)",
                    }
                )

        return actions
