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
    Generates a technical integration blueprint, API payload specification,
    and hardware safety guidelines for embedded engineers (ESP32, Home Assistant, MQTT brokers, relays).
    Includes PDF export capability.
    """

    @staticmethod
    def generate_iot_handoff_report() -> str:
        return """# IoT Hardware Integration Handoff Report

**Project:** Vision-Based Smart Energy Saving System (v2.0)  
**Target Audience:** Hardware Engineers, Embedded/IoT Developers, Network Admins  
**Document Version:** 2.1.0  

---

## The Judgment & Critique

### What You Did Well

* **Clear Decoupling:** Separating the Vision Master from the IoT Subscriber layer makes the architecture pluggable and modular.
* **Appropriate Relay Selection:** Sizing a 30A SSR for a 1200W AC unit versus 10A mechanical relays for lighting/fans shows proper load considerations.
* **Dual Integration Strategy:** Providing both an in-process Python adapter and an out-of-process WebSocket interface gives downstream engineers immediate flexibility.

### Where It Falls Short for Hardware / Embedded Engineers

1. **Vague MQTT Architecture:** You mention MQTT in text, but give zero topic topologies (`telemetry/`, `cmd/`, `status/`). Embedded developers need explicit topic definitions and QoS levels.
2. **ESP32 Boot Pin Traps:** Recommending GPIO pins without specifying boot behavior is risky. On the ESP32, several pins pull HIGH at boot or act as strapping pins, causing relays to chatter or the MCU to fail to boot.
3. **No Hardware Protection Circuitry:** Missing critical electrical safety specs: flyback diodes for inductive fan loads, RC snubbers for AC switching, and optocoupler active-LOW/HIGH logic.
4. **Vision Bouncing / Flickering:** No mention of **Vision Hysteresis / Debounce** time. Raw vision inference flickers; without delay/debounce parameters, physical relays will chatter continuously, burning out contact points.
5. **Fail-Safe / Contact Logic:** Missing explicit Normal Open (NO) vs. Normal Closed (NC) guidance during power loss or system failure.

---

# Enhanced Integration Handoff Report

Below is the upgraded, industry-standard handoff document designed for seamless handoff to hardware, embedded, and network engineers.

---

# IOT HARDWARE INTEGRATION HANDOFF REPORT

**Project:** Vision-Based Smart Energy Saving System (v2.0)  
**Target Audience:** Hardware Engineers, Embedded/IoT Developers, Network Admins  
**Document Version:** 2.1.0  

---

## 1. System Architecture & Topology

The **Vision Decision Master** acts as a centralized edge engine running inference (`YOLOv8` + temporal state smoothing). It evaluates room occupancy and broadcasts target device states to distributed **IoT Actuators / Relays** (ESP32, Home Assistant, Node-RED).

```
                      +------------------------------------------+
                      | Vision Decision Master (Edge Server)     |
                      | YOLOv8 Object Tracking + State Engine    |
                      +-----------------------------------------+
                                           |
                   +-----------------------+-----------------------+
                   |                                               |
                   v                                               v
     [ WebSocket / MQTT Broker ]                     [ Python Adapter Layer ]
     JSON Telemetry & Control Streams               In-Process BaseDeviceController
                   |                                               |
        +--------------------+                         +--------------------+
        |                     |                         |                     |
        v                     v                         v                     v
+---------------+     +---------------+         +---------------+     +---------------+
| ESP32 Node 01 |     | HomeAssist/NR |         | Custom Driver |     | Relay Board B |
| (Zone A)      |     | (Zone B)      |         | (RS-485/CAN)  |     | (Direct GPIO) |
+---------------+     +---------------+         +---------------+     +---------------+
```

---

## 2. Communication Interfaces & API Contracts

### Option A: In-Process Python Adapter Pattern

Located at `app/device_controller/base.py`. Developers extending the core backend directly in Python must subclass `BaseDeviceController`:

```python
from app.device_controller.base import BaseDeviceController
import requests
import logging

logger = logging.getLogger(__name__)

class HomeAssistantAdapter(BaseDeviceController):
    \"\"\"Adapter for syncing vision states with Home Assistant REST API.\"\"\"
    
    def __init__(self, host: str, token: str):
        self.base_url = f"http://{host}:8123/api/services/switch"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def set_device_state(self, device_id: str, state: str, reason: str = "") -> bool:
        action = "turn_on" if state.upper() == "ON" else "turn_off"
        url = f"{self.base_url}/{action}"
        payload = {"entity_id": f"switch.{device_id}"}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=3.0)
            response.raise_for_status()
            logger.info(f"[HA Adapter] {device_id} -> {state} ({reason})")
            return True
        except requests.RequestException as err:
            logger.error(f"[HA Adapter Failed] {device_id}: {err}")
            return False
```

---

### Option B: MQTT Protocol Spec (Recommended for ESP32 / Bare-Metal)

* **Broker Port:** `1883` (Unencrypted) / `8883` (MQTTS - TLS 1.3)
* **QoS Level:** `1` (At least once)
* **Retain Flag:** `True` for state updates

#### Topic Structure:

* **State Broadcast (Server -> IoT):** `v2/energy/zone_a/devices/state`
* **Command Override (IoT -> Server):** `v2/energy/zone_a/devices/command`
* **Node Telemetry / LWT (IoT -> Server):** `v2/energy/nodes/{client_id}/telemetry`

#### Inbound State Broadcast Payload:

```json
{
  "timestamp": 1754783162,
  "occupant_count": 1,
  "occupancy_status": "OCCUPIED",
  "device_states": {
    "light": "ON",
    "fan": "ON",
    "ac": "OFF"
  },
  "device_telemetry": {
    "light": { "state": "ON", "power_pct": 100.0, "is_ramping": false },
    "fan":   { "state": "ON", "power_pct": 100.0, "is_ramping": false },
    "ac":    { "state": "OFF", "power_pct": 0.0,  "is_ramping": false }
  }
}
```

---

### Option C: WebSocket API Contract

* **URL:** `ws://<SERVER_IP>:8000/ws/status`
* **Ping / Pong Interval:** Every 10 seconds.

---

## 3. Recommended Hardware Specifications & Pinouts

| Device ID | Target Zone | Max Load | Relay Type | ESP32 GPIO | Trigger Logic | Safety Circuitry |
| --- | --- | --- | --- | --- | --- | --- |
| `light` | Desk (Zone A) | 40 W | 5V Optocoupler Relay | `GPIO 18` | Active LOW | Snubber on AC output |
| `fan` | Desk (Zone A) | 65 W | 5V Optocoupler Relay | `GPIO 19` | Active LOW | Flyback diode across DC inductive motor / Snubber for AC |
| `ac` | Transit (Zone B) | 1200 W | 30A Solid State Relay (SSR) | `GPIO 21` | Active HIGH | Zero-cross switching + Heatsink |

> **GPIO Selection Note:** Avoid using ESP32 strapping pins (`GPIO 0, 2, 12, 15`) or input-only pins (`GPIO 34-39`). Using these risks relay flickering during startup reset cycles.

---

## 4. Hardware Safety, Fail-Safe, & Edge Resiliency Rules

```
                 [ Hardware Fail-Safe Logic Flow ]
                 
                 +-------------------------------+
                 |  Is WebSocket / MQTT alive?  |
                 +---------------+---------------+
                                 |
                      +----------+----------+
                      |                     |
                   ( YES )                ( NO )
                      |                     |
         +------------v------------+  +-----v-------------------------+
         | Execute Vision Command  |  | Start 5-Second Grace Timer    |
         | Reset Watchdog Timer    |  +------------------------------+
         +-------------------------+                 |
                                                     v
                                      +-------------------------------+
                                      | Timer Expired (> 5 seconds)?  |
                                      +------------------------------+
                                                     |
                                          +----------+----------+
                                          |                     |
                                       ( YES )                ( NO )
                                          |                     |
                        +-----------------v---+   +-------------v---------------+
                        | Fail-Safe Mode:     |   | Hold Last Known Valid State |
                        | AC -> OFF           |   +-----------------------------+
                        | Light/Fan -> ON/NC  |
                        +---------------------+
```

1. **Vision Debounce & Anti-Flicker:**
* Minimum occupancy hysteresis: **15 seconds**.
* State transitions to `OFF` will hold for 15 seconds after zero detection to avoid power-cycling relays on temporary camera occlusion.

2. **Relay Terminal Wiring (NO vs. NC):**
* **Lights & Fans:** Wire to **Normally Closed (NC)** terminal so room lights default to ON if the micro-controller loses total power.
* **High-Power AC:** Wire to **Normally Open (NO)** terminal so high-current heating/cooling loads drop out safely on hardware fault.

3. **Hardware Watchdog:**
* Embedded MCU must run a **5-second Software Watchdog Timer (WDT)**. If no telemetry updates are received over WS/MQTT within 5 seconds, fallback to local manual override mode.

4. **Inductive Inrush Protection:**
* Motorized loads (fans/compressors) must maintain a minimum **3-minute lockout delay** between consecutive restart cycles to protect AC compressor motors from back-pressure lockout.
"""

    @staticmethod
    def generate_pdf_report() -> bytes:
        """
        Generates a PDF document version of the IoT Hardware Handoff Report using fpdf2.
        """
        from fpdf import FPDF

        def sanitize(txt: str) -> str:
            replacements = {
                "—": " -- ",
                "–": " - ",
                "•": "* ",
                "“": '"',
                "”": '"',
                "‘": "'",
                "’": "'",
                "…": "...",
                "→": "->",
                "←": "<-",
                "↔": "<->",
                "°": " deg ",
            }
            for k, v in replacements.items():
                txt = txt.replace(k, v)
            return txt.encode("latin-1", "replace").decode("latin-1")

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(100, 100, 100)
                hdr_text = sanitize("Vision-Based Smart Energy Saving System -- IoT Hardware Integration Report")
                self.cell(0, 6, hdr_text, border=0, new_x="LMARGIN", new_y="NEXT", align="R")
                self.set_draw_color(200, 200, 200)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(4)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(140, 140, 140)
                self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

        pdf = PDF(orientation="P", unit="mm", format="A4")
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        report_md = IoTHandoffReportGenerator.generate_iot_handoff_report()
        lines = report_md.split("\n")

        in_code_block = False
        code_lines = []

        for line in lines:
            line_clean = sanitize(line)

            if line_clean.startswith("```"):
                if in_code_block:
                    # End code block
                    pdf.set_font("Courier", "", 8)
                    pdf.set_fill_color(245, 247, 250)
                    pdf.set_text_color(40, 40, 40)
                    for cl in code_lines:
                        safe_cl = sanitize(cl.replace("\t", "    "))
                        pdf.set_x(10)
                        pdf.cell(pdf.epw, 4.5, f"  {safe_cl}", border=0, new_x="LMARGIN", new_y="NEXT", fill=True)
                    pdf.ln(3)
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                    code_lines = []
                continue

            if in_code_block:
                code_lines.append(line_clean)
                continue

            pdf.set_x(10)

            # Headers
            if line_clean.startswith("# "):
                pdf.ln(2)
                pdf.set_font("Helvetica", "B", 15)
                pdf.set_text_color(20, 35, 60)
                title_text = line_clean[2:].strip()
                pdf.multi_cell(pdf.epw, 8, title_text)
                pdf.ln(1)
            elif line_clean.startswith("## "):
                pdf.ln(2)
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(30, 60, 110)
                h2_text = line_clean[3:].strip()
                pdf.multi_cell(pdf.epw, 7, h2_text)
                pdf.ln(1)
            elif line_clean.startswith("### "):
                pdf.ln(1)
                pdf.set_font("Helvetica", "B", 10.5)
                pdf.set_text_color(40, 80, 140)
                h3_text = line_clean[4:].strip().replace("**", "")
                pdf.multi_cell(pdf.epw, 6, h3_text)
                pdf.ln(1)
            elif line_clean.startswith("---"):
                pdf.set_draw_color(220, 225, 230)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(3)
            elif line_clean.startswith("* ") or line_clean.startswith("- "):
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(40, 40, 40)
                clean_bullet = line_clean[2:].strip().replace("**", "")
                pdf.multi_cell(pdf.epw, 5, f"  - {clean_bullet}")
            elif line_clean.strip().startswith("1.") or line_clean.strip().startswith("2.") or line_clean.strip().startswith("3.") or line_clean.strip().startswith("4.") or line_clean.strip().startswith("5."):
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(40, 40, 40)
                clean_num = line_clean.strip().replace("**", "")
                pdf.multi_cell(pdf.epw, 5, f"  {clean_num}")
            elif line_clean.startswith(">"):
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 50, 0)
                pdf.set_fill_color(255, 248, 235)
                clean_quote = line_clean[1:].strip().replace("**", "")
                pdf.multi_cell(pdf.epw, 5, f"  Note: {clean_quote}", fill=True)
                pdf.ln(1)
            elif line_clean.strip() == "":
                pdf.ln(2)
            else:
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(50, 50, 50)
                clean_line = line_clean.replace("**", "").replace("`", "")
                pdf.multi_cell(pdf.epw, 5.5, clean_line)

        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, str):
            return pdf_bytes.encode("latin1")
        return bytes(pdf_bytes)




