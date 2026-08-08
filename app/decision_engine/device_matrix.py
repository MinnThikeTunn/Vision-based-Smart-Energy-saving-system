from typing import Any, Dict, List, Optional
from app.decision_engine.state_machine import RoomState


class DeviceControlMatrix:
    """
    Device Control Matrix for automated per-device and per-zone state management.
    
    Supports:
    - Spatial ROI zone assignment (e.g. Zone A -> Light, Fan; Zone B -> AC)
    - Independent device shutdown timeouts
    - Zone-specific occupancy control (vacant zone devices turn OFF)
    """

    def __init__(
        self,
        device_timeouts: Dict[str, float],
        zone_device_map: Optional[Dict[str, List[str]]] = None,
    ):
        """
        device_timeouts e.g.: {'light': 5, 'fan': 10, 'ac': 10}
        zone_device_map e.g.: {'Zone A (Desk)': ['light', 'fan'], 'Zone B (Transit)': ['ac']}
        """
        self.device_timeouts = device_timeouts
        self.zone_device_map = zone_device_map or {
            "Zone A (Desk)": ["light", "fan"],
            "Zone B (Transit)": ["ac"],
        }

    def evaluate(
        self,
        room_state: RoomState,
        empty_duration_sec: float,
        current_states: Dict[str, str],
        active_zones: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        if room_state == RoomState.OCCUPIED:
            active_set = set(active_zones) if active_zones is not None else None

            for device_id, timeout in self.device_timeouts.items():
                current_state = current_states.get(device_id, "OFF").upper()

                # Determine if device belongs to an active zone or whole-room default
                is_zone_active = True
                if active_set is not None:
                    # Check if device is mapped to any active zone
                    mapped_zones = [z for z, devs in self.zone_device_map.items() if device_id in devs]
                    if mapped_zones:
                        is_zone_active = any(z in active_set for z in mapped_zones)

                if is_zone_active and current_state != "ON":
                    actions.append(
                        {
                            "device_id": device_id,
                            "action": "TURN_ON",
                            "reason": f"Occupant detected in assigned active zone",
                        }
                    )
                elif not is_zone_active and current_state != "OFF":
                    actions.append(
                        {
                            "device_id": device_id,
                            "action": "TURN_OFF",
                            "reason": f"Zone vacant, shutting down device",
                        }
                    )

        elif room_state == RoomState.EMPTY:
            for device_id, timeout in self.device_timeouts.items():
                current_state = current_states.get(device_id, "OFF").upper()
                if empty_duration_sec >= timeout and current_state != "OFF":
                    actions.append(
                        {
                            "device_id": device_id,
                            "action": "TURN_OFF",
                            "reason": f"Room empty for {empty_duration_sec:.0f}s (timeout: {timeout:.0f}s)",
                        }
                    )

        return actions
