from typing import Any
import asyncio
import contextlib
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.decision_engine.device_matrix import DeviceControlMatrix
from app.decision_engine.state_machine import OccupancyStateMachine
from app.detector.pipeline import VisionPipeline
from app.device_controller.base import BaseDeviceController
from app.device_controller.simulation import SimulationController

router = APIRouter(tags=["websocket"])

_device_controller: BaseDeviceController = SimulationController()
_state_machine: OccupancyStateMachine = OccupancyStateMachine()
_device_matrix: DeviceControlMatrix = DeviceControlMatrix(
    device_timeouts={"light": 180, "fan": 600, "ac": 600}
)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        for connection in self.active_connections:
            with contextlib.suppress(Exception):
                await connection.send_json(message)


manager = ConnectionManager()


def get_device_controller() -> BaseDeviceController:
    return _device_controller


def build_telemetry_payload(pipeline: VisionPipeline | None = None) -> dict[str, Any]:
    raw_count = 0
    if pipeline is not None:
        _, raw_count = pipeline.get_latest_processed()

    current_time = time.time()
    snapshot = _state_machine.update(raw_count, current_time)

    # Evaluate device control matrix
    current_states = _device_controller.get_device_states()
    actions = _device_matrix.evaluate(
        room_state=snapshot.state,
        empty_duration_sec=snapshot.empty_duration_sec,
        current_states=current_states,
    )

    for action in actions:
        target_state = "ON" if action["action"] == "TURN_ON" else "OFF"
        _device_controller.set_device_state(
            device_id=action["device_id"],
            state=target_state,
            reason=action["reason"],
        )

    return {
        "occupant_count": snapshot.occupant_count,
        "occupancy_status": snapshot.state.value,
        "empty_duration_sec": round(snapshot.empty_duration_sec, 1),
        "seconds_until_empty": round(snapshot.seconds_until_empty, 1),
        "device_states": _device_controller.get_device_states(),
        "event_logs": _device_controller.get_event_logs(limit=20),
    }


@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            # Check for incoming client messages with timeout
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                payload = json.loads(data)
                if payload.get("type") == "TOGGLE_DEVICE":
                    device_id = payload.get("device_id")
                    target_state = payload.get("state", "OFF")
                    if device_id:
                        _device_controller.set_device_state(
                            device_id=device_id,
                            state=target_state,
                            reason="Manual dashboard override",
                        )
            except asyncio.TimeoutError:
                pass

            # Push telemetry snapshot
            telemetry = build_telemetry_payload()
            await websocket.send_json(telemetry)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
