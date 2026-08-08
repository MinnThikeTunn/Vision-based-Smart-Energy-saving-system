
This roadmap extends the **Technical Expansion Specification (July 2026)**. 


```

```
                              EXECUTION FLOW

```

┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│   Phases 0 - 3    │ ──> │   Phases 4 - 7    │ ──> │      Phase 8      │
│ Proof, CI & Trust │     │ Core CV & Systems │     │ Differentiation   │
└───────────────────┘     └───────────────────┘     └───────────────────┘

```

* **Phases 0–3:** Close the gap between implemented code and README/demo claims while building a privacy-first narrative.
* **Phases 4–7:** Re-sequence the original Computer Vision, Analytics, Architecture, and UX pillars by effort-to-impact ratio.
* **Phase 8:** Add stand-out features to set this project apart from standard occupancy-detection projects on GitHub.

---

## 🚀 Phase 0: Proof & Presentation
> **Priority:** `P0 (Do First)` | **Focus:** Elevating perceived quality with zero core engineering cost.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Honest README Realignment** | `S` | `README.md` | Align README claims directly with implemented features (ROI zones, telemetry, tracking) to maintain technical credibility. |
| **System Architecture Diagram** | `S` | `docs/architecture.md` | Add a native **Mermaid** diagram mapping: <br>`Camera` → `Detector` → `Tracker` → `State Machine` → `Device Matrix` → `WebSocket` → `Dashboard`. |
| **Quantified Impact Section** | `M` | `README.md`<br>`docs/results.md` | Highlight 1 week of local testing metrics: **Occupancy Accuracy %**, **kWh Saved vs. Baseline**, and **FPS Performance**. |

---

## 🛠️ Phase 2: Simulation Realism & Software-Only Differentiators
> **Priority:** `P0` | **Focus:** Making the hardware abstraction layer production-grade without physical dependencies.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Realistic Device Dynamics** | `M` | `app/device_controller/simulation.py` | Model startup/shutdown latency, non-instant power ramp curves, and simulated failure/timeout responses. |
| **Stateful Command Logging** | `S` | `app/device_controller/simulation.py`<br>`app/device_controller/base.py` | Log explicit confirmation and failure states for every command instead of assuming success. |
| **Pluggable Adapter Docs** | `S` | `README.md`<br>`app/device_controller/base.py` | Document the `base.py` adapter interface clearly to prove the system is plug-and-play for physical hardware. |
| **One-Command Bootstrap** | `S` | `scripts/setup.sh` | Replace Docker dependency with a lightweight `setup.sh` / `setup.ps1` script (`venv` + install + run). |

---

## 🔒 Phase 3: Privacy & Trust Architecture
> **Priority:** `P1` | **Focus:** Proactively addressing privacy concerns inherent to vision-based monitoring.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Data Retention Policy** | `S` | `docs/privacy.md`<br>`README.md` | Formally document that no raw video frames are saved—only lightweight derived telemetry and vector coordinates. |
| **Headless Automation Mode** | `M` | `app/api/video_router.py`<br>`settings.yaml` | Add a runtime configuration flag to disable video feed streaming while maintaining full detection logic. |
| **Canvas Anonymization** | `M` | `app/detector/pipeline.py` | *(Optional)* Apply real-time face blurring/redaction on output overlay streams. |

---

## 👁️ Phase 4: Advanced Computer Vision & Spatial Intelligence
> **Priority:** `P2` | **Focus:** Transitioning from basic binary detection to spatial awareness.


```

```
   [ Camera Feed ]
          │
          ▼

```

┌─────────────────────┐
│ YOLOv8 Pose / Track │
└──────────┬──────────┘
│
┌───────┴───────┐
▼               ▼
[ Zone A: Desk ]  [ Zone B: Transit ]
(Active Use)      (Passive Walkby)
│               │
▼               ▼
Keep ON          Stay OFF

```

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Spatial ROI Matrix** | `M` | `app/detector/person_detector.py`<br>`app/decision_engine/device_matrix.py` | Implement polygon/bounding zones in camera space to allow per-zone control instead of whole-room switches. |
| **Device-to-Zone Mapping** | `M` | `app/decision_engine/device_matrix.py` | Map detection centroids directly to specific relays inside `device_matrix.py`. |
| **Pose-Aware Filtering** | `L` | `app/detector/person_detector.py` | Integrate `yolov8n-pose.pt` keypoints to differentiate active desk work from passive walking transit. |
| **Multi-Object Tracking** | `M` | `app/detector/pipeline.py`<br>`app/detector/tracker.py` | Implement **ByteTrack** or **DeepSORT** to maintain persistent IDs across transient detection drops. |
| **Per-Zone Debounce** | `S` | `app/decision_engine/state_machine.py` | Extend state machine grace periods (`OFF_DELAY`) independently across individual zones. |

---

## 📊 Phase 5: Smart Analytics & Quantifiable Impact Engine
> **Priority:** `P2` | **Focus:** Translating detection states into financial and environmental metrics.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Device Wattage Mapping** | `S` | `app/config/settings.yaml`<br>`app/config/schema.py` | Define rated power consumption profiles per device category in configuration files. |
| **Real-time ROI Engine** | `M` | `app/analytics/energy_calculator.py` | Calculate cumulative **kWh**, **Cost ($)**, and **CO2e** savings against an always-on baseline. |
| **Tiered State Management** | `M` | `app/decision_engine/device_matrix.py` | Support tri-state power levels: `ACTIVE (100%)` → `IDLE/DIM (30%)` → `SLEEP (0%)`. |
| **Dynamic Tariff Config** | `S` | `app/config/settings.yaml` | Support configurable local electricity rates with documented sources instead of static defaults. |

---

## ⚡ Phase 6: Edge Architecture & System Performance
> **Priority:** `P3` | **Focus:** Optimizing system throughput, latency, and observability.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Async Frame Pipeline** | `M` | `app/detector/pipeline.py` | Decouple frame acquisition from ML inference via background queues with adaptive frame skipping. |
| **Model Acceleration** | `L` | `scripts/export_onnx.py`<br>`app/detector/person_detector.py` | Export PyTorch models to **ONNX Runtime** (and TensorRT for Jetson targets) with benchmark reporting. |
| **System Observability** | `M` | `app/main.py`<br>`app/telemetry/metrics.py` | Implement structured logging (`structlog`) and expose a native Prometheus `/metrics` endpoint. |

---

## 🎨 Phase 7: Interactive Dashboard & Control Center
> **Priority:** `P3` | **Focus:** Delivering a high-impact interface for real-time monitoring and management.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Overlaid Video Stream** | `M` | `app/static/index.html`<br>`app/api/video_router.py` | Render live spatial zones, tracking IDs, keypoints, and state flags onto the web UI. |
| **Interactive ROI Editor** | `L` | `app/static/index.html`<br>`app/api/config_router.py` | Build a drag-and-drop UI zone builder that updates configurations without manual YAML editing. |
| **Manual Override System** | `M` | `app/api/ws_router.py`<br>`app/decision_engine/state_machine.py` | Implement real-time WebSocket overrides with timed automated recovery logic. |
| **Live Telemetry Charts** | `M` | `app/static/index.html` | Embed interactive time-series visualizers (Chart.js) driven by Phase 5 calculation streams. |

---

## 🌟 Phase 8: Portfolio Differentiators
> **Priority:** `P4` | **Focus:** Stand-out capabilities beyond traditional rule-based occupancy systems.


```

```
   [ Historical Logs ]
            │
            ▼

```

┌───────────────────────────┐
│ Predictive Time-Series    │
└─────────────┬─────────────┘
│
▼
[ Pre-warm HVAC / Lighting ]
(Before Scheduled Arrival)

```

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Predictive Occupancy** | `L` | `app/analytics/occupancy_forecast.py` | Apply time-series forecasting to pre-warm HVAC and lighting before predicted peak arrivals. |
| **Multi-Camera Fusion** | `L` | `app/detector/pipeline.py`<br>`app/decision_engine/state_machine.py` | Aggregate spatial occupancy across multiple stream inputs into a single zone state engine. |
| **Automated Facilities Reports**| `M` | `app/analytics/report_generator.py` | Export downloadable weekly summary reports (PDF/CSV) detailing energy ROI and usage trends. |
| **Audit Log API** | `M` | `app/api/config_router.py` | Maintain versioned settings history and audit logs for configuration adjustments over time. |

---

## 📅 Recommended Execution Order


```

[ Week 1 ]  ──>  Phase 0: Proof & Presentation
[ Week 2 ]  ──>  Phase 1: One-Command Setup & CI Bootstrap
[ Week 3 ]  ──>  Phase 2: Simulation & Pluggable Adapter Docs
[ Week 4 ]  ──>  Phase 4 & Phase 5: CV Tracking + ROI Analytics Engine
[ Week 5 ]  ──>  Phase 6 & Phase 7: Edge Runtime + Dashboard UI
[ Week 6 ]  ──>  Phase 3: Privacy Documentation
[ Week 7 ]  ──>  Phase 8: Predictive Occupancy Forecasting (Differentiator)

```

---

## ✅ Definition of Done ("Portfolio Ready")

- [ ] **Demonstrated ROI:** README features a live demonstration GIF alongside verified energy saving metrics ($/kWh).
- [ ] **Zero-Friction Setup:** Full stack launches cleanly via a single local bootstrap script (`scripts/setup.sh`).
- [ ] **Production Simulation:** Device controller handles latencies, power curves, and responses via documented interfaces.
- [ ] **Automated CI:** GitHub Actions build, lint, and test suites are consistently passing.
- [ ] **Privacy-First:** Dedicated privacy documentation is explicitly linked in primary documentation.
- [ ] **Real-Time Visualization:** Dashboard tracks live power dynamics alongside bounding spatial zones.
"""

file_path = "ROADMAP_v2.md"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Successfully generated {file_path}")


```

```text
Successfully generated ROADMAP_v2.md


```

Your Markdown file is ready!

Below is the raw Markdown content for convenient copy-pasting or direct use in your repository:

```markdown
# Vision-Based Smart Energy Saving System — Roadmap v2
### Engineering Blueprint + Differentiation Plan
**Repo:** `MinnThikeTunn/Vision-based-Smart-Energy-saving-system`  
**Date:** July 2026

---

## 0. How to Read This Roadmap

This roadmap extends the **Technical Expansion Specification (July 2026)**. 


```

```
                              EXECUTION FLOW

```

┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│   Phases 0 - 3    │ ──> │   Phases 4 - 7    │ ──> │      Phase 8      │
│ Proof, CI & Trust │     │ Core CV & Systems │     │ Differentiation   │
└───────────────────┘     └───────────────────┘     └───────────────────┘

```

* **Phases 0–3:** Close the gap between implemented code and README/demo claims while building a privacy-first narrative.
* **Phases 4–7:** Re-sequence the original Computer Vision, Analytics, Architecture, and UX pillars by effort-to-impact ratio.
* **Phase 8:** Add stand-out features to set this project apart from standard occupancy-detection projects on GitHub.

---

## 🚀 Phase 0: Proof & Presentation
> **Priority:** `P0 (Do First)` | **Focus:** Elevating perceived quality with zero core engineering cost.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Honest README Realignment** | `S` | `README.md` | Align README claims directly with implemented features (ROI zones, telemetry, tracking) to maintain technical credibility. |
| **System Architecture Diagram** | `S` | `docs/architecture.md` | Add a native **Mermaid** diagram mapping: <br>`Camera` → `Detector` → `Tracker` → `State Machine` → `Device Matrix` → `WebSocket` → `Dashboard`. |
| **Quantified Impact Section** | `M` | `README.md`<br>`docs/results.md` | Highlight 1 week of local testing metrics: **Occupancy Accuracy %**, **kWh Saved vs. Baseline**, and **FPS Performance**. |

---

## 🛠️ Phase 2: Simulation Realism & Software-Only Differentiators
> **Priority:** `P0` | **Focus:** Making the hardware abstraction layer production-grade without physical dependencies.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Realistic Device Dynamics** | `M` | `app/device_controller/simulation.py` | Model startup/shutdown latency, non-instant power ramp curves, and simulated failure/timeout responses. |
| **Stateful Command Logging** | `S` | `app/device_controller/simulation.py`<br>`app/device_controller/base.py` | Log explicit confirmation and failure states for every command instead of assuming success. |
| **Pluggable Adapter Docs** | `S` | `README.md`<br>`app/device_controller/base.py` | Document the `base.py` adapter interface clearly to prove the system is plug-and-play for physical hardware. |
| **One-Command Bootstrap** | `S` | `scripts/setup.sh` | Replace Docker dependency with a lightweight `setup.sh` / `setup.ps1` script (`venv` + install + run). |

---

## 🔒 Phase 3: Privacy & Trust Architecture
> **Priority:** `P1` | **Focus:** Proactively addressing privacy concerns inherent to vision-based monitoring.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Data Retention Policy** | `S` | `docs/privacy.md`<br>`README.md` | Formally document that no raw video frames are saved—only lightweight derived telemetry and vector coordinates. |
| **Headless Automation Mode** | `M` | `app/api/video_router.py`<br>`settings.yaml` | Add a runtime configuration flag to disable video feed streaming while maintaining full detection logic. |
| **Canvas Anonymization** | `M` | `app/detector/pipeline.py` | *(Optional)* Apply real-time face blurring/redaction on output overlay streams. |

---

## 👁️ Phase 4: Advanced Computer Vision & Spatial Intelligence
> **Priority:** `P2` | **Focus:** Transitioning from basic binary detection to spatial awareness.


```

```
   [ Camera Feed ]
          │
          ▼

```

┌─────────────────────┐
│ YOLOv8 Pose / Track │
└──────────┬──────────┘
│
┌───────┴───────┐
▼               ▼
[ Zone A: Desk ]  [ Zone B: Transit ]
(Active Use)      (Passive Walkby)
│               │
▼               ▼
Keep ON          Stay OFF

```

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Spatial ROI Matrix** | `M` | `app/detector/person_detector.py`<br>`app/decision_engine/device_matrix.py` | Implement polygon/bounding zones in camera space to allow per-zone control instead of whole-room switches. |
| **Device-to-Zone Mapping** | `M` | `app/decision_engine/device_matrix.py` | Map detection centroids directly to specific relays inside `device_matrix.py`. |
| **Pose-Aware Filtering** | `L` | `app/detector/person_detector.py` | Integrate `yolov8n-pose.pt` keypoints to differentiate active desk work from passive walking transit. |
| **Multi-Object Tracking** | `M` | `app/detector/pipeline.py`<br>`app/detector/tracker.py` | Implement **ByteTrack** or **DeepSORT** to maintain persistent IDs across transient detection drops. |
| **Per-Zone Debounce** | `S` | `app/decision_engine/state_machine.py` | Extend state machine grace periods (`OFF_DELAY`) independently across individual zones. |

---

## 📊 Phase 5: Smart Analytics & Quantifiable Impact Engine
> **Priority:** `P2` | **Focus:** Translating detection states into financial and environmental metrics.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Device Wattage Mapping** | `S` | `app/config/settings.yaml`<br>`app/config/schema.py` | Define rated power consumption profiles per device category in configuration files. |
| **Real-time ROI Engine** | `M` | `app/analytics/energy_calculator.py` | Calculate cumulative **kWh**, **Cost ($)**, and **CO2e** savings against an always-on baseline. |
| **Tiered State Management** | `M` | `app/decision_engine/device_matrix.py` | Support tri-state power levels: `ACTIVE (100%)` → `IDLE/DIM (30%)` → `SLEEP (0%)`. |
| **Dynamic Tariff Config** | `S` | `app/config/settings.yaml` | Support configurable local electricity rates with documented sources instead of static defaults. |

---

## ⚡ Phase 6: Edge Architecture & System Performance
> **Priority:** `P3` | **Focus:** Optimizing system throughput, latency, and observability.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Async Frame Pipeline** | `M` | `app/detector/pipeline.py` | Decouple frame acquisition from ML inference via background queues with adaptive frame skipping. |
| **Model Acceleration** | `L` | `scripts/export_onnx.py`<br>`app/detector/person_detector.py` | Export PyTorch models to **ONNX Runtime** (and TensorRT for Jetson targets) with benchmark reporting. |
| **System Observability** | `M` | `app/main.py`<br>`app/telemetry/metrics.py` | Implement structured logging (`structlog`) and expose a native Prometheus `/metrics` endpoint. |

---

## 🎨 Phase 7: Interactive Dashboard & Control Center
> **Priority:** `P3` | **Focus:** Delivering a high-impact interface for real-time monitoring and management.

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Overlaid Video Stream** | `M` | `app/static/index.html`<br>`app/api/video_router.py` | Render live spatial zones, tracking IDs, keypoints, and state flags onto the web UI. |
| **Interactive ROI Editor** | `L` | `app/static/index.html`<br>`app/api/config_router.py` | Build a drag-and-drop UI zone builder that updates configurations without manual YAML editing. |
| **Manual Override System** | `M` | `app/api/ws_router.py`<br>`app/decision_engine/state_machine.py` | Implement real-time WebSocket overrides with timed automated recovery logic. |
| **Live Telemetry Charts** | `M` | `app/static/index.html` | Embed interactive time-series visualizers (Chart.js) driven by Phase 5 calculation streams. |

---

## 🌟 Phase 8: Portfolio Differentiators
> **Priority:** `P4` | **Focus:** Stand-out capabilities beyond traditional rule-based occupancy systems.


```

```
   [ Historical Logs ]
            │
            ▼

```

┌───────────────────────────┐
│ Predictive Time-Series    │
└─────────────┬─────────────┘
│
▼
[ Pre-warm HVAC / Lighting ]
(Before Scheduled Arrival)

```

| Task | Effort | Target Files | Objective & Value |
| :--- | :---: | :--- | :--- |
| **Predictive Occupancy** | `L` | `app/analytics/occupancy_forecast.py` | Apply time-series forecasting to pre-warm HVAC and lighting before predicted peak arrivals. |
| **Multi-Camera Fusion** | `L` | `app/detector/pipeline.py`<br>`app/decision_engine/state_machine.py` | Aggregate spatial occupancy across multiple stream inputs into a single zone state engine. |
| **Automated Facilities Reports**| `M` | `app/analytics/report_generator.py` | Export downloadable weekly summary reports (PDF/CSV) detailing energy ROI and usage trends. |
| **Audit Log API** | `M` | `app/api/config_router.py` | Maintain versioned settings history and audit logs for configuration adjustments over time. |

---

## 📅 Recommended Execution Order


```

[ Week 1 ]  ──>  Phase 0: Proof & Presentation
[ Week 2 ]  ──>  Phase 1: One-Command Setup & CI Bootstrap
[ Week 3 ]  ──>  Phase 2: Simulation & Pluggable Adapter Docs
[ Week 4 ]  ──>  Phase 4 & Phase 5: CV Tracking + ROI Analytics Engine
[ Week 5 ]  ──>  Phase 6 & Phase 7: Edge Runtime + Dashboard UI
[ Week 6 ]  ──>  Phase 3: Privacy Documentation
[ Week 7 ]  ──>  Phase 8: Predictive Occupancy Forecasting (Differentiator)

```

---

## ✅ Definition of Done ("Portfolio Ready")

- [ ] **Demonstrated ROI:** README features a live demonstration GIF alongside verified energy saving metrics ($/kWh).
- [ ] **Zero-Friction Setup:** Full stack launches cleanly via a single local bootstrap script (`scripts/setup.sh`).
- [ ] **Production Simulation:** Device controller handles latencies, power curves, and responses via documented interfaces.
- [ ] **Automated CI:** GitHub Actions build, lint, and test suites are consistently passing.
- [ ] **Privacy-First:** Dedicated privacy documentation is explicitly linked in primary documentation.
- [ ] **Real-Time Visualization:** Dashboard tracks live power dynamics alongside bounding spatial zones.

```
