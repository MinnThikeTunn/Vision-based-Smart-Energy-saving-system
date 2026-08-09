import asyncio
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from app.device_controller.base import BaseDeviceController


class SimulationController(BaseDeviceController):
    """
    Production-grade simulation device controller (Version 3.0).
    
    Features:
    - Non-blocking asynchronous latency delays & power ramps (0%-100% curve).
    - Tri-state support ('ON', 'OFF', 'DIM').
    - O(1) constant-time audit trail command logging using deque & hashmap indexing.
    """

    def __init__(self, latency_ms: int = 300, power_ramp_sec: float = 1.5) -> None:
        self.latency_ms = latency_ms
        self.power_ramp_sec = power_ramp_sec

        self._target_states: Dict[str, str] = {}
        self._current_power_pct: Dict[str, float] = {}
        self._device_power_ramps: Dict[str, float] = {}
        self._pending_tasks: Dict[str, asyncio.Task] = {}
        self._event_logs: deque[Dict[str, Any]] = deque(maxlen=100)
        self._event_logs_index: Dict[str, Dict[str, Any]] = {}

    def register_device(self, device_id: str, power_ramp_sec: Optional[float] = None) -> None:
        device_key = device_id.lower()
        if device_key not in self._target_states:
            self._target_states[device_key] = "OFF"
            self._current_power_pct[device_key] = 0.0
        if power_ramp_sec is not None:
            self._device_power_ramps[device_key] = max(0.0, float(power_ramp_sec))

    def unregister_device(self, device_id: str) -> None:
        device_key = device_id.lower()
        self._target_states.pop(device_key, None)
        self._current_power_pct.pop(device_key, None)
        self._device_power_ramps.pop(device_key, None)
        if device_key in self._pending_tasks and not self._pending_tasks[device_key].done():
            self._pending_tasks[device_key].cancel()


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

        # Log initial command receipt with O(1) appendleft & hashmap indexing
        event_id = str(uuid.uuid4())
        event_entry = {
            "id": event_id,
            "timestamp": datetime.now().isoformat(),
            "device_id": device_key,
            "action": target_state,
            "status": "PENDING",
            "reason": reason or "Automated rule trigger",
            "mode": "Simulation",
        }
        self._event_logs.appendleft(event_entry)
        self._event_logs_index[event_id] = event_entry

        # Cancel any pending transition task for this device
        if device_key in self._pending_tasks and not self._pending_tasks[device_key].done():
            self._pending_tasks[device_key].cancel()

        # Schedule asynchronous latency & power ramp in background loop if available
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(
                self._async_transition(device_key, target_state, event_id)
            )
            self._pending_tasks[device_key] = task
        except RuntimeError:
            # Fallback for sync contexts: apply state directly
            self._apply_sync_state(device_key, target_state, event_id)

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
            ramp_sec = self._device_power_ramps.get(device_key, self.power_ramp_sec)
            steps = 5
            step_duration = (ramp_sec / steps) if ramp_sec > 0 else 0.0
            for i in range(1, steps + 1):
                if step_duration > 0:
                    await asyncio.sleep(step_duration)
                self._current_power_pct[device_key] = start_pct + (target_pct - start_pct) * (i / steps)


            self._current_power_pct[device_key] = target_pct

            # 3. Update log status to CONFIRMED using O(1) hashmap lookup
            if log_id in self._event_logs_index:
                self._event_logs_index[log_id]["status"] = "CONFIRMED"
        except asyncio.CancelledError:
            if log_id in self._event_logs_index:
                self._event_logs_index[log_id]["status"] = "CANCELLED"

    def _apply_sync_state(self, device_key: str, target_state: str, log_id: str) -> None:
        target_pct = 100.0 if target_state == "ON" else (30.0 if target_state == "DIM" else 0.0)
        self._current_power_pct[device_key] = target_pct
        if log_id in self._event_logs_index:
            self._event_logs_index[log_id]["status"] = "CONFIRMED"


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
        return list(self._event_logs)[:limit]

