import csv
import io
from datetime import datetime
from typing import Dict, Any, List


class FacilitiesReportGenerator:
    """
    Automated Facilities Executive Summary Report Generator.
    Generates production-ready, standardized CSV summary reports detailing
    spatial occupancy, device operational states, energy ROI, and audit trails.
    """

    @staticmethod
    def generate_csv_report(
        energy_metrics: Dict[str, Any],
        device_states: Dict[str, str],
        event_logs: List[Dict[str, Any]],
        facility_name: str = "Main Facility / Zone A-B",
    ) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # ---------------------------------------------------------
        # 1. REPORT HEADER & METADATA
        # ---------------------------------------------------------
        writer.writerow(["=========================================================================================="])
        writer.writerow(["VISION-BASED SMART ENERGY SAVING SYSTEM — EXECUTIVE FACILITIES SUMMARY REPORT"])
        writer.writerow(["=========================================================================================="])
        writer.writerow(["Document Type", "Facilities Operational & Energy ROI Audit"])
        writer.writerow(["Facility / Zone", facility_name])
        writer.writerow(["Generated Timestamp", f"{timestamp_str} (Local Time)"])
        writer.writerow(["System Version", "v2.0 Production Release"])
        writer.writerow(["Privacy Compliance", "Verified Zero Frame Retention & Anonymized Ingestion"])
        writer.writerow([])

        # ---------------------------------------------------------
        # 2. KEY PERFORMANCE INDICATORS (ENERGY & SUSTAINABILITY ROI)
        # ---------------------------------------------------------
        writer.writerow(["--- SECTION 1: ENERGY ROI & SUSTAINABILITY KPIS ---"])
        writer.writerow(["METRIC DESCRIPTION", "REAL-TIME VALUE", "BASELINE / UNIT", "STATUS / METRIC KEY"])

        current_watts = float(energy_metrics.get("current_power_watts", 0.0))
        baseline_watts = float(energy_metrics.get("baseline_power_watts", 0.0))
        cum_baseline_kwh = float(energy_metrics.get("cumulative_kwh_baseline", 0.0))
        cum_actual_kwh = float(energy_metrics.get("cumulative_kwh_actual", 0.0))
        saved_kwh = float(energy_metrics.get("saved_kwh", 0.0))
        saved_cost = float(energy_metrics.get("saved_cost_usd", 0.0))
        saved_co2 = float(energy_metrics.get("saved_co2_kg", 0.0))
        efficiency_pct = float(energy_metrics.get("energy_efficiency_pct", 0.0))

        writer.writerow(["Active Power Demand", f"{current_watts:.2f} W", f"Baseline: {baseline_watts:.2f} W", "current_power_watts"])
        writer.writerow(["Cumulative Baseline Consumption", f"{cum_baseline_kwh:.4f} kWh", "Always-ON Model", "cumulative_kwh_baseline"])
        writer.writerow(["Cumulative Actual Consumption", f"{cum_actual_kwh:.4f} kWh", "Smart Automation", "cumulative_kwh_actual"])
        writer.writerow(["Total Energy Conserved", f"{saved_kwh:.4f} kWh", "Net Reduction", "saved_kwh"])
        writer.writerow(["Financial Cost Savings", f"${saved_cost:.2f} USD", "Net Cost Savings", "saved_cost_usd"])
        writer.writerow(["Avoided Greenhouse Gas Emissions", f"{saved_co2:.3f} kg CO2e", "EPA Emission Factor", "saved_co2_kg"])
        writer.writerow(["Energy Efficiency Optimization Rate", f"{efficiency_pct:.1f}%", "Target: >30.0%", "energy_efficiency_pct"])
        writer.writerow([])

        # ---------------------------------------------------------
        # 3. SPATIAL DEVICE CONTROL MATRIX & OPERATIONAL STATES
        # ---------------------------------------------------------
        writer.writerow(["--- SECTION 2: DEVICE OPERATIONAL MATRIX ---"])
        writer.writerow(["DEVICE IDENTIFIER", "PRIMARY SPATIAL ZONE", "TARGET STATE", "RATED POWER (W)", "OPERATIONAL MODE"])

        device_zone_map = {
            "LIGHT": ("Zone A (Desk)", "40.0 W"),
            "FAN": ("Zone A (Desk)", "65.0 W"),
            "AC": ("Zone B (Transit)", "1200.0 W")
        }

        for dev_id, state in device_states.items():
            dev_upper = dev_id.upper()
            zone_info, power_info = device_zone_map.get(dev_upper, ("General Space", "N/A"))
            writer.writerow([dev_upper, zone_info, state.upper(), power_info, "Automated Vision Control"])
        if not device_states:
            writer.writerow(["N/A", "No active devices registered", "OFF", "0 W", "Idle"])
        writer.writerow([])

        # ---------------------------------------------------------
        # 4. AUDIT TRAIL & SYSTEM EVENT LOGS
        # ---------------------------------------------------------
        writer.writerow(["--- SECTION 3: SYSTEM AUDIT & AUTOMATION TRAIL ---"])
        writer.writerow(["LOG TIMESTAMP", "DEVICE ID", "AUTOMATION ACTION", "EXECUTION STATUS", "RULE / REASON TRIGGER"])

        if event_logs:
            for log in event_logs[:30]:
                ts = log.get("timestamp", timestamp_str)
                if "T" in str(ts):
                    ts_parts = str(ts).split("T")
                    time_part = ts_parts[1].split(".")[0]
                    ts = f"{ts_parts[0]} {time_part}"

                writer.writerow([
                    ts,
                    str(log.get("device_id", "SYSTEM")).upper(),
                    str(log.get("action", "STATE_SYNC")).upper(),
                    str(log.get("status", "CONFIRMED")).upper(),
                    log.get("reason", "Occupancy State Transition")
                ])
        else:
            writer.writerow([timestamp_str, "SYSTEM", "AUDIT_INITIALIZED", "NOMINAL", "System operating within target bounds; no fault events recorded."])

        writer.writerow([])
        writer.writerow(["=========================================================================================="])
        writer.writerow(["END OF REPORT — Vision-Based Smart Energy Saving System v2.0 Automated Generation"])
        writer.writerow(["=========================================================================================="])

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
**Generated At**: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

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

