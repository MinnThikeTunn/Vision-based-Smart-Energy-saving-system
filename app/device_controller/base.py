from typing import Any


class BaseDeviceController:
    def set_device_state(self, device_id: str, state: str, reason: str = "") -> bool:
        raise NotImplementedError

    def get_device_states(self) -> dict[str, str]:
        raise NotImplementedError

    def get_event_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        raise NotImplementedError
