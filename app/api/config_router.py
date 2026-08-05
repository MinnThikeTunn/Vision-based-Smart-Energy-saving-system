from datetime import datetime
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Response
from app.config.loader import load_settings, save_settings
from app.config.schema import SystemConfiguration
from app.analytics.report_generator import FacilitiesReportGenerator, IoTHandoffReportGenerator

router = APIRouter(prefix="/api", tags=["config"])

_config_audit_logs: List[Dict[str, Any]] = []


@router.get("/config", response_model=SystemConfiguration)
def get_config() -> SystemConfiguration:
    return load_settings()


@router.post("/config", response_model=SystemConfiguration)
def update_config(new_config: SystemConfiguration) -> SystemConfiguration:
    try:
        save_settings(new_config)

        # Log configuration version update into audit log
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "CONFIG_UPDATE",
            "details": f"Updated settings (Confidence: {new_config.detector.confidence_threshold}, Empty Timeout: {new_config.occupancy.empty_timeout_sec}s, Headless: {new_config.privacy.headless_mode})",
        }
        _config_audit_logs.insert(0, audit_entry)
        if len(_config_audit_logs) > 50:
            _config_audit_logs.pop()

        return new_config
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/audit_logs")
def get_config_audit_logs() -> List[Dict[str, Any]]:
    return _config_audit_logs


@router.get("/reports/download")
def download_facilities_report() -> Response:
    from app.api.ws_router import get_energy_calculator, get_device_controller
    calculator = get_energy_calculator()
    controller = get_device_controller()

    device_states = controller.get_device_states()
    device_telemetry = controller.get_device_telemetry()
    energy_metrics = calculator.update(device_states, device_telemetry)
    event_logs = controller.get_event_logs()

    csv_content = FacilitiesReportGenerator.generate_csv_report(
        energy_metrics=energy_metrics,
        device_states=device_states,
        event_logs=event_logs,
    )

    filename = f"facilities_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/reports/iot_handoff")
def download_iot_handoff_report() -> Response:
    markdown_content = IoTHandoffReportGenerator.generate_iot_handoff_report()
    filename = "iot_hardware_handoff_report.md"
    return Response(
        content=markdown_content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
