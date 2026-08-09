from typing import Any, Dict
import asyncio
import contextlib
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.decision_engine.device_matrix import DeviceControlMatrix
from app.decision_engine.state_machine import OccupancyStateMachine, RoomState
from app.detector.pipeline import VisionPipeline
from app.device_controller.base import BaseDeviceController
from app.device_controller.simulation import SimulationController
from app.analytics.energy_calculator import EnergyCalculator
from app.analytics.energy_logger import EnergyLogger
from app.analytics.energy_engine import EnergyAnalyticsEngine
from app.analytics.occupancy_forecast import OccupancyForecaster
from app.telemetry.metrics import get_metrics_registry

router = APIRouter(tags=["websocket"])

_device_controller: BaseDeviceController = SimulationController()
_state_machine: OccupancyStateMachine = OccupancyStateMachine()
_device_matrix: DeviceControlMatrix = DeviceControlMatrix(
    device_timeouts={}, zone_device_map={}
)
_energy_calculator: EnergyCalculator = EnergyCalculator()
_energy_logger: EnergyLogger = EnergyLogger()
_analytics_engine: EnergyAnalyticsEngine = EnergyAnalyticsEngine(logger=_energy_logger)
_forecaster: OccupancyForecaster = OccupancyForecaster()

# Recover cumulative baseline and actual energy from today's CSV logs
_recovered = _energy_logger.recover_todays_energy()
_energy_calculator.cumulative_kwh_baseline = _recovered.get("cumulative_kwh_baseline", 0.0)
_energy_calculator.cumulative_kwh_actual = _recovered.get("cumulative_kwh_actual", 0.0)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        for connection in self.active_connections:
            with contextlib.suppress(Exception):
                await connection.send_json(message)


manager = ConnectionManager()


def get_device_controller() -> BaseDeviceController:
    return _device_controller


def get_energy_calculator() -> EnergyCalculator:
    return _energy_calculator


def get_energy_logger() -> EnergyLogger:
    return _energy_logger


def get_analytics_engine() -> EnergyAnalyticsEngine:
    return _analytics_engine



def build_telemetry_payload(pipeline: VisionPipeline | None = None) -> Dict[str, Any]:
    from app.config.loader import load_settings
    try:
        settings = load_settings()
        _state_machine.persistence_window_sec = settings.occupancy.persistence_window_sec
        _state_machine.empty_timeout_sec = settings.occupancy.empty_timeout_sec

        device_timeouts = {}
        wattages = {}
        current_config_keys = set()
        for device_name, rule in settings.devices.items():
            if rule.enabled:
                device_key = device_name.lower()
                current_config_keys.add(device_key)
                device_timeouts[device_key] = rule.empty_shutdown_timeout_sec
                wattages[device_key] = rule.rated_wattage
                if hasattr(_device_controller, "register_device"):
                    _device_controller.register_device(device_key, rule.power_ramp_sec)

        # Unregister deleted devices
        if hasattr(_device_controller, "unregister_device"):
            existing_states = _device_controller.get_device_states()
            for dev_key in list(existing_states.keys()):
                if dev_key not in current_config_keys:
                    _device_controller.unregister_device(dev_key)

        zone_map = {}
        for zone in settings.spatial_zones:
            zone_map[zone.name] = [d.lower() for d in zone.assigned_devices]

        _device_matrix.device_timeouts = device_timeouts
        _device_matrix.zone_device_map = zone_map
        _energy_calculator.device_wattages = wattages
        _energy_calculator.electricity_rate_kwh = settings.analytics.electricity_rate_kwh
        _energy_calculator.co2_per_kwh_kg = settings.analytics.co2_per_kwh_kg
    except Exception as e:
        print(f"Error updating config in telemetry payload: {e}")


    raw_count = 0
    active_zones = None
    if pipeline is not None:
        _, raw_count, active_zones = pipeline.get_latest_processed()

    current_time = time.time()
    snapshot = _state_machine.update(raw_count, current_time)

    current_states = _device_controller.get_device_states()
    current_telemetry = _device_controller.get_device_telemetry()

    # Evaluate device control matrix with active spatial zones
    actions = _device_matrix.evaluate(
        room_state=snapshot.state,
        empty_duration_sec=snapshot.empty_duration_sec,
        current_states=current_states,
        active_zones=active_zones,
    )

    for action in actions:
        target_state = "ON" if action["action"] == "TURN_ON" else ("DIM" if action["action"] == "DIM" else "OFF")
        _device_controller.set_device_state(
            device_id=action["device_id"],
            state=target_state,
            reason=action["reason"],
        )

    # Calculate real-time energy & ROI analytics
    energy_metrics = _energy_calculator.update(current_states, current_telemetry)

    # Log 5-minute time-series snapshot for 24-hour analytics
    if _energy_logger.should_log():
        _energy_logger.log_snapshot(
            energy_metrics=energy_metrics,
            device_states=current_states,
            occupant_count=snapshot.occupant_count,
        )


    # Calculate occupancy forecast
    forecast = _forecaster.predict_next_hour()

    # Update Prometheus metrics registry
    fps_val = pipeline.fps_target if pipeline else 30.0
    metrics_registry = get_metrics_registry()
    metrics_registry.update_telemetry(
        fps=fps_val,
        occupant_count=snapshot.occupant_count,
        room_status=snapshot.state.value,
        device_states=current_states,
        energy_metrics=energy_metrics,
    )

    device_countdowns = {}
    try:
        for device_id, rule in settings.devices.items():
            if not rule.enabled:
                device_countdowns[device_id] = 0.0
            elif snapshot.state == RoomState.OCCUPIED:
                device_countdowns[device_id] = rule.empty_shutdown_timeout_sec
            else:
                current_state = current_states.get(device_id, "OFF").upper()
                if current_state == "OFF":
                    device_countdowns[device_id] = 0.0
                else:
                    device_countdowns[device_id] = max(0.0, round(rule.empty_shutdown_timeout_sec - snapshot.empty_duration_sec, 1))
    except Exception as ex:
        print(f"Error calculating device countdowns: {ex}")

    return {
        "occupant_count": snapshot.occupant_count,
        "occupancy_status": snapshot.state.value,
        "empty_duration_sec": round(snapshot.empty_duration_sec, 1),
        "seconds_until_empty": round(snapshot.seconds_until_empty, 1),
        "device_states": current_states,
        "device_telemetry": current_telemetry,
        "device_countdowns": device_countdowns,
        "energy_metrics": energy_metrics,
        "forecast": forecast,
        "event_logs": _device_controller.get_event_logs(limit=20),
    }


@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    from app.api.video_router import get_vision_pipeline
    try:
        while True:
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

            telemetry = build_telemetry_payload(get_vision_pipeline())
            await websocket.send_json(telemetry)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
