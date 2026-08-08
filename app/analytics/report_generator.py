import csv
import io
from datetime import datetime
from typing import Dict, Any, List


class FacilitiesReportGenerator:
    """
    Automated Facilities Report Generator.
    Generates downloadable CSV summary reports detailing energy ROI and usage metrics.
    """

    @staticmethod
    def generate_csv_report(
        energy_metrics: Dict[str, Any],
        device_states: Dict[str, str],
        event_logs: List[Dict[str, Any]],
    ) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        # Header section
        writer.writerow(["VISION-BASED SMART ENERGY SAVING SYSTEM — FACILITIES SUMMARY REPORT"])
        writer.writerow(["Generated At", datetime.now().isoformat()])
        writer.writerow([])

        # Summary KPIs
        writer.writerow(["METRIC", "VALUE"])
        writer.writerow(["Current Power Draw (Watts)", energy_metrics.get("current_power_watts", 0)])
        writer.writerow(["Baseline Power Draw (Watts)", energy_metrics.get("baseline_power_watts", 0)])
        writer.writerow(["Cumulative Baseline (kWh)", energy_metrics.get("cumulative_kwh_baseline", 0)])
        writer.writerow(["Cumulative Actual (kWh)", energy_metrics.get("cumulative_kwh_actual", 0)])
        writer.writerow(["Total kWh Saved", energy_metrics.get("saved_kwh", 0)])
        writer.writerow(["Total Cost Saved ($)", energy_metrics.get("saved_cost_usd", 0)])
        writer.writerow(["CO2 Emissions Prevented (kg)", energy_metrics.get("saved_co2_kg", 0)])
        writer.writerow(["Efficiency Gain (%)", f"{energy_metrics.get('energy_efficiency_pct', 0)}%"])
        writer.writerow([])

        # Active Device States
        writer.writerow(["DEVICE ID", "TARGET STATE"])
        for dev, state in device_states.items():
            writer.writerow([dev.upper(), state])
        writer.writerow([])

        # Recent Event Audit Log
        writer.writerow(["AUDIT LOG TRAIL"])
        writer.writerow(["Timestamp", "Device", "Action", "Status", "Reason"])
        for log in event_logs[:20]:
            writer.writerow(
                [
                    log.get("timestamp", ""),
                    log.get("device_id", ""),
                    log.get("action", ""),
                    log.get("status", "CONFIRMED"),
                    log.get("reason", ""),
                ]
            )

        return output.getvalue()


class IoTHandoffReportGenerator:
    """
    IoT Team Handoff Report Generator.
    Generates a technical integration blueprint and API payload specification
    for hardware engineers (ESP32, Home Assistant, MQTT brokers, Tuya, Zigbee relays).
    """

    @staticmethod
    def generate_iot_handoff_report() -> str:
        return """# IOT HARDWARE INTEGRATION HANDOFF REPORT

**Project**: Vision-Based Smart Energy Saving System (v2.0)  
**Target Audience**: Hardware Engineers, Embedded/IoT Developers, Network Admins  
**Generated At**: """ + datetime.now().isoformat() + """

---

## 1. Executive Summary & Interface Architecture

This system acts as an **Edge Vision Decision Master** that publishes real-time device target states based on occupancy detection. The IoT hardware layer operates as a **Pluggable Subscriber / Actuator** receiving commands to control physical relays (Light, Fan, Air Conditioner).

```
┌───────────────────────────────┐        WebSocket / MQTT        ┌──────────────────────────────┐
│  Vision Decision Master       │ ─────────────────────────────> │  IoT Smart Relays / ESP32    │
│  (YOLOv8 + State Machine)     │ <───────────────────────────── │  (Home Assistant / GPIO)     │
└───────────────────────────────┘       Telemetry Confirmation   └──────────────────────────────┘
```

---

## 2. Interface Options for IoT Hardware Integration

### Option A: Subclass `BaseDeviceController` (Python In-Process Adapter)
Located in [`app/device_controller/base.py`](file:///D:/cvProject/app/device_controller/base.py).

Subclass `BaseDeviceController` and override `set_device_state`:
```python
from app.device_controller.base import BaseDeviceController
import requests # or paho.mqtt.client

class HomeAssistantAdapter(BaseDeviceController):
    def set_device_state(self, device_id: str, state: str, reason: str = "") -> bool:
        # Example HTTP POST to Home Assistant REST API or MQTT broker
        url = f"http://homeassistant.local:8123/api/services/switch/turn_{state.lower()}"
        headers = {"Authorization": "Bearer YOUR_LONG_LIVED_TOKEN"}
        payload = {"entity_id": f"switch.{device_id}"}
        requests.post(url, json=payload, headers=headers)
        return True
```

### Option B: WebSocket / MQTT / HTTP API Payload Schema (Remote IoT Device / ESP32 / Node-RED)
Connect to the WebSocket endpoint:
* **URL**: `ws://<SERVER_IP>:8000/ws/status`
* **Protocol**: Standard JSON WebSockets

#### Inbound Telemetry Payload Schema (Server -> IoT Sub):
```json
{
  "occupant_count": 1,
  "occupancy_status": "Occupied",
  "device_states": {
    "light": "ON",
    "fan": "ON",
    "ac": "OFF"
  },
  "device_telemetry": {
    "light": {"state": "ON", "power_pct": 100.0, "is_ramping": false},
    "fan": {"state": "ON", "power_pct": 100.0, "is_ramping": false},
    "ac": {"state": "OFF", "power_pct": 0.0, "is_ramping": false}
  }
}
```

#### Outbound Command Payload Schema (IoT -> Server Override):
```json
{
  "type": "TOGGLE_DEVICE",
  "device_id": "light",
  "state": "OFF"
}
```

---

## 3. Recommended Pinout & Relay Specifications

| Device ID | Zone | Rated Power (W) | Relay Specification | ESP32 GPIO Pin (Suggested) |
| :--- | :--- | :--- | :--- | :--- |
| `light` | Zone A (Desk) | 40 W | 5V / 10A Optocoupler Relay Module | `GPIO 18` |
| `fan` | Zone A (Desk) | 65 W | 5V / 10A Optocoupler Relay Module | `GPIO 19` |
| `ac` | Zone B (Transit) | 1200 W | 30A High-Power Solid State Relay (SSR) | `GPIO 21` |

---

## 4. Operational & Fail-Safe Guidelines

1. **Hardware Heartbeat**: IoT hardware should maintain a 5-second watch-dog timer. If WebSocket connection drops, keep current state or default to safe state.
2. **State Confirmation**: Log confirmed state updates in event audit trails.
3. **Power Ramps**: Motorized/Inverter loads (e.g. AC) should handle soft-start ramps natively to prevent inrush current spikes.
"""
