from typing import Any, Dict, List


class BaseDeviceController:
    """
    Abstract Hardware Adapter Interface for Smart Energy Saving System.
    
    Subclass this interface to connect real physical devices or IoT protocols
    (e.g., Home Assistant REST API, MQTT broker, Zigbee, Tuya, ESP32 Relays).
    """

    def set_device_state(self, device_id: str, state: str, reason: str = "") -> bool:
        """
        Trigger a device state transition (e.g. 'ON', 'OFF', 'DIM').
        Returns True if action was initiated or queued, False otherwise.
        """
        raise NotImplementedError

    def get_device_states(self) -> Dict[str, str]:
        """
        Retrieve discrete target states for all registered devices.
        Returns mapping of device_id -> 'ON'/'OFF'/'DIM'.
        """
        raise NotImplementedError

    def get_device_telemetry(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve detailed real-time telemetry (power %, actual state, latency status).
        """
        raise NotImplementedError

    def get_event_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve stateful event log audit trail.
        """
        raise NotImplementedError
