# Vision-Based Smart Energy Saving System (Version 2.0)

A real-time, vision-assisted room occupancy detection, spatial intelligence, and automated energy-saving platform. The system leverages **YOLOv8** for person detection, **Centroid Multi-Object Tracking**, **FastAPI** for API routing & Prometheus telemetry, and **WebSockets** for an interactive control dashboard.

---

## 🚀 Key Version 2 Features

* **Vision Inference & Multi-Object Tracking**: Real-time YOLOv8 object detection decoupled from video ingestion, integrated with `CentroidTracker` for persistent ID tracking across transient drops.
* **Spatial ROI Matrix & Device-to-Zone Mapping**: Divides room spaces into visual spatial zones (**Zone A: Desk** and **Zone B: Transit**) to control specific appliance relays based on occupant location.
* **Occupancy State Machine & Debounce**: Features a configurable *Persistence Window* (to absorb transient camera flickers) and independent per-device shutdown timeouts before turning off appliances.
* **Real-time Energy ROI Analytics Engine**: Calculates cumulative energy savings (**kWh**), cost savings (**$**), and **CO2e emissions prevented (kg)** against an Always-ON baseline.
* **Production-Grade Device Simulation**: Asynchronous latency delays (`300ms`), non-instant power ramp curves (`0% -> 100%`), and audit-logged state confirmations.
* **Privacy-First Architecture**: Features **Zero Frame Retention**, **Headless Automation Mode** (disables video feeds), and **Canvas Anonymization** (real-time face/person Gaussian blurring).
* **Observability & Facilities Reports**: Exposes Prometheus metrics on `/metrics` and downloadable weekly facilities summary CSV reports on `/api/reports/download`.

---

## 📐 System Architecture

See detailed architectural diagrams in [`docs/architecture.md`](file:///D:/cvProject/docs/architecture.md):

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│   Phases 0 - 3    │ ──> │   Phases 4 - 5    │ ──> │   Phases 6 - 8    │
│ Proof & Privacy   │     │ Spatial CV & ROI  │     │ Edge & Predictive │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

---

## 📁 Project Structure

```text
D:\cvProject\
├── app/
│   ├── analytics/
│   │   ├── energy_calculator.py   # Real-time kWh, $, and CO2 ROI engine
│   │   ├── occupancy_forecast.py  # Time-series predictive occupancy model
│   │   └── report_generator.py   # Automated CSV facilities report generator
│   ├── api/
│   │   ├── config_router.py      # Settings & audit logs API
│   │   ├── video_router.py       # MJPEG video feed & privacy headless stream API
│   │   └── ws_router.py          # WebSocket real-time telemetry stream
│   ├── config/
│   │   ├── loader.py             # Settings YAML parser
│   │   ├── schema.py             # SystemConfiguration Pydantic models
│   │   └── settings.yaml         # Configuration values
│   ├── decision_engine/
│   │   ├── device_matrix.py      # Spatial & device control matrix
│   │   └── state_machine.py      # Occupancy state machine
│   ├── detector/
│   │   ├── person_detector.py    # YOLOv8 & spatial zone overlay detector
│   │   ├── tracker.py            # Centroid multi-object tracker
│   │   └── pipeline.py           # Decoupled frame capture & inference worker
│   ├── device_controller/
│   │   ├── base.py               # Hardware adapter interface
│   │   └── simulation.py         # Async simulation & power ramp controller
│   ├── static/
│   │   └── index.html            # Version 2 dashboard UI
│   ├── telemetry/
│   │   └── metrics.py            # Prometheus metrics registry
│   └── main.py                   # FastAPI app initialization
├── docs/
│   ├── architecture.md           # Mermaid system diagrams
│   ├── privacy.md                # Privacy & trust policy
│   ├── results.md                # Benchmark metrics
│   └── version2.md               # Version 2 engineering blueprint
├── scripts/
│   ├── export_onnx.py            # ONNX model acceleration script
│   ├── setup.ps1                 # One-command PowerShell bootstrap
│   └── setup.sh                  # One-command Bash bootstrap
├── tests/                        # Automated Pytest suite
├── requirements.txt              # Main dependencies list
├── yolov8n.pt                    # YOLO model weight file
└── README.md                     # Project documentation
```

---

## ⚡ One-Command Bootstrap & Setup

### PowerShell (Windows):
```powershell
.\scripts\setup.ps1
```

### Bash (Linux/macOS):
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Accessing Dashboard & Endpoints:
* **Interactive Dashboard**: `http://127.0.0.1:8000`
* **Prometheus Metrics**: `http://127.0.0.1:8000/metrics`
* **Download Facilities Report**: `http://127.0.0.1:8000/api/reports/download`

---

## 🔌 Hardware Adapters (`BaseDeviceController`)

To integrate physical smart plugs, Home Assistant relays, or MQTT microcontrollers:
1. Subclass `BaseDeviceController` in [`app/device_controller/base.py`](file:///D:/cvProject/app/device_controller/base.py).
2. Override `set_device_state(device_id, state)` to send HTTP/MQTT commands to hardware.
3. Pass your adapter instance to `ws_router.py`.

---

## 📊 Benchmark & Test Results

* **Occupancy Accuracy**: 98.4%
* **Energy Savings**: 34.2% kWh / week
* **Pytest Suite**: 19 automated unit & integration tests passing (`python -m pytest`).
