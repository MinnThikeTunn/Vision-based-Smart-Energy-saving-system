import asyncio
from datetime import datetime
from typing import Any, Dict, List
import uuid
from app.device_controller.base import BaseDeviceController


class SimulationController(BaseDeviceController):
    """
    Production-grade simulation device controller.
    
    Features:
    - Non-blocking asynchronous latency delays & power ramps (0%-100% curve).
    - Tri-state support ('ON', 'OFF', 'DIM').
    - Audit trail command logging with explicit confirmation.
    """

    def __init__(self, latency_ms: int = 300, power_ramp_sec: float = 1.5) -> None:
        self.latency_ms = latency_ms
        self.power_ramp_sec = power_ramp_sec

        self._target_states: Dict[str, str] = {
            "light": "OFF",
            "fan": "OFF",
            "ac": "OFF",
        }
        self._current_power_pct: Dict[str, float] = {
            "light": 0.0,
            "fan": 0.0,
            "ac": 0.0,
        }
        self._pending_tasks: Dict[str, asyncio.Task] = {}
        self._event_logs: List[Dict[str, Any]] = []

    def set_device_state(self, device_id: str, state: str, reason: str = "") -> bool:
        device_key = device_id.lower()
        target_state = state.upper()
        if device_key not in self._target_states:
            self._target_states[device_key] = "OFF"
            self._current_power_pct[device_key] = 0.0

        previous_target = self._target_states.get(device_key, "OFF")
        if previous_target == target_state:
            return False  # Prevent redundant command triggers

        self._target_states[device_key] = target_state

        # Log initial command receipt
        event_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "device_id": device_key,
            "action": target_state,
            "status": "PENDING",
            "reason": reason or "Automated rule trigger",
            "mode": "Simulation",
        }
        self._event_logs.insert(0, event_entry)
        if len(self._event_logs) > 100:
            self._event_logs.pop()

        # Cancel any pending transition task for this device
        if device_key in self._pending_tasks and not self._pending_tasks[device_key].done():
            self._pending_tasks[device_key].cancel()

        # Schedule asynchronous latency & power ramp in background loop if available
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(
                self._async_transition(device_key, target_state, event_entry["id"])
            )
            self._pending_tasks[device_key] = task
        except RuntimeError:
            # Fallback for sync contexts: apply state directly
            self._apply_sync_state(device_key, target_state, event_entry["id"])

        return True

    async def _async_transition(self, device_key: str, target_state: str, log_id: str) -> None:
        try:
            # 1. Simulate network/hardware latency delay asynchronously
            if self.latency_ms > 0:
                await asyncio.sleep(self.latency_ms / 1000.0)

            # Determine target power percentage
            target_pct = 100.0 if target_state == "ON" else (30.0 if target_state == "DIM" else 0.0)
            start_pct = self._current_power_pct.get(device_key, 0.0)

            # 2. Simulate non-instant power ramp curve asynchronously
            steps = 5
            step_duration = (self.power_ramp_sec / steps) if self.power_ramp_sec > 0 else 0.0
            for i in range(1, steps + 1):
                if step_duration > 0:
                    await asyncio.sleep(step_duration)
                self._current_power_pct[device_key] = start_pct + (target_pct - start_pct) * (i / steps)

            self._current_power_pct[device_key] = target_pct

            # 3. Update log status to CONFIRMED
            for entry in self._event_logs:
                if entry.get("id") == log_id:
                    entry["status"] = "CONFIRMED"
                    break
        except asyncio.CancelledError:
            for entry in self._event_logs:
                if entry.get("id") == log_id:
                    entry["status"] = "CANCELLED"
                    break

    def _apply_sync_state(self, device_key: str, target_state: str, log_id: str) -> None:
        target_pct = 100.0 if target_state == "ON" else (30.0 if target_state == "DIM" else 0.0)
        self._current_power_pct[device_key] = target_pct
        for entry in self._event_logs:
            if entry.get("id") == log_id:
                entry["status"] = "CONFIRMED"
                break

    def get_device_states(self) -> Dict[str, str]:
        return self._target_states.copy()

    def get_device_telemetry(self) -> Dict[str, Dict[str, Any]]:
        telemetry = {}
        for dev, state in self._target_states.items():
            telemetry[dev] = {
                "state": state,
                "power_pct": round(self._current_power_pct.get(dev, 0.0), 1),
                "is_ramping": (
                    dev in self._pending_tasks and not self._pending_tasks[dev].done()
                ),
            }
        return telemetry

    def get_event_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._event_logs[:limit]
