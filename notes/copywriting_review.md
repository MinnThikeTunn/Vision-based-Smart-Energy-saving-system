# UX Copywriting & Microcopy Audit & Line-by-Line Rewrite

**Audited System**: Vision-Based Smart Energy Saving System (v2.0)  
**Target Repository**: `D:\cvProject`  
**Auditor Persona**: Torrey Podmajersky & Joanna Wiebe Hybrid (UX Copywriting, Microcopy & Conversion Clarity Expert)  
**Date**: August 9, 2026  

---

## 1. Executive Summary & Strategic Voice Profile

### Voice Profile & Principles
To deliver maximum clarity for building operations managers while maintaining technical precision for hardware engineers, the copy must follow four fundamental UX copy tenets:
1. **Clear Over Clever**: Prefer immediate clarity over technical jargon or flashy marketing buzzwords.
2. **Predictable Action Microcopy**: Buttons and interactive controls must explicitly describe *what happens next* (e.g., replace vague `"Toggle"` with `"Turn On"` / `"Turn Off"`).
3. **Transparent & Empathetic Error Recovery**: Error states must explain *what went wrong*, *why*, and *how the user can recover* — avoiding raw JavaScript stack trace dumping.
4. **Humanized Metric Telemetry**: Translate internal ML model implementation details (such as `"YOLO Person Count"` or `"Elapsed Zero Count"`) into plain facility management concepts (`"People Detected"`, `"Time Empty"`).

---

## 2. Section 1: UI Copy, Microcopy & Label Audit (`app/static/index.html`)

### 2.1 Header & System Navigation Bar

| Line Range | Original Copy | Weakness / Anti-Pattern | Rewritten Copy (Torrey & Joanna Standards) |
| :--- | :--- | :--- | :--- |
| **L97–L99** | `Real-Time AI Occupancy Detection & Automated Energy Automation` | Redundant phrase ("Automated Energy Automation"). | `Real-Time Occupancy Detection & Intelligent Energy Automation` |
| **L111** | `<i class="fa-solid fa-tv"></i> Live Control Center` | Functional, but slightly generic. | `<i class="fa-solid fa-tv"></i> Live Dashboard` |
| **L118** | `<i class="fa-solid fa-sliders"></i> Settings & Analytics Hub` | Wordy label for secondary navigation tab. | `<i class="fa-solid fa-sliders"></i> Settings & Analytics` |
| **L127** | `<i class="fa-solid fa-list-check"></i> Audit Logs` | Functional label, but missing descriptive clarity. | `<i class="fa-solid fa-list-check"></i> Activity Audit Log` |
| **L137** | `Connecting...` | Lacks context on what the system is connecting to. | `Connecting to room sensor...` |
| **L737 (JS)** | `Disconnected` | Doesn't reassure user or explain auto-reconnect. | `Connection Lost — Reconnecting...` |

---

### 2.2 Spatial Feed & Telemetry Cards

| Line Range | Original Copy | Weakness / Anti-Pattern | Rewritten Copy (Torrey & Joanna Standards) |
| :--- | :--- | :--- | :--- |
| **L153** | `Live Spatial Video Feed` | Technical jargon ("Spatial Video"). | `Live Room Camera Feed` |
| **L161** | `Heatmap OFF` / `Heatmap ON` | Binary label without clear state indicator. | `Occupancy Heatmap: OFF` / `Occupancy Heatmap: ON` |
| **L167** | `+ Draw Zone & Add Device` | Compound action phrase on single button. | `+ Add Spatial Zone & Device` |
| **L187** | Card Header: `Occupants` | Clean header, but subtext uses ML jargon. | `People in Room` |
| **L189** | Card Subtext: `YOLO Person Count` | **Internal ML Jargon**: Exposes YOLO algorithm name to end user. | Subtext: `Live Camera Count` |
| **L194** | Card Header: `Room Status` | Subtext is repetitive (`Occupancy State`). | Subtext: `Current Room State` |
| **L201** | Card Header: `Empty Duration` | Subtext: `Elapsed Zero Count`. **Developer Loop Variable** leaked to UI. | Header: `Time Unoccupied`<br>Subtext: `Duration without occupants` |
| **L208** | Card Header: `Room Countdown` | Subtext lists raw timer abbreviations. | Header: `Auto Shutdown Timers`<br>Subtext: `Countdown until auto-off` |

---

### 2.3 Virtual Devices & Dynamic Controls

| Line Range | Original Copy | Weakness / Anti-Pattern | Rewritten Copy (Torrey & Joanna Standards) |
| :--- | :--- | :--- | :--- |
| **L224** | `Virtual Devices & Power Ramps` | Engineering term ("Power Ramps") confuses facility operators. | `Connected Devices & Power Control` |
| **L228** | `Reset Defaults` | Vague button text. Reset what defaults? | `Reset to Default Devices` |
| **L239** | `Zero Active Devices Configured` | Cold, robotic error state header. | `No Smart Devices Connected` |
| **L240–L242** | `Click below to draw a spatial zone on the camera feed and bind a new smart device.` | Passive instructions. | `Draw a zone on the video feed above to pair your first smart device.` |
| **L245** | `+ Create First Zone & Device` | Double verb on button. | `+ Draw First Zone` |
| **L831** | `Toggle` | **Ambiguous Button Microcopy**: User cannot predict if clicking will turn ON or OFF. | State-aware button copy:<br>`state === "ON" ? "Turn Off" : "Turn On"` |

---

### 2.4 Settings & Rule Configurator

| Line Range | Original Copy | Weakness / Anti-Pattern | Rewritten Copy (Torrey & Joanna Standards) |
| :--- | :--- | :--- | :--- |
| **L310** | `Persistence Window (s)` | **Developer Jargon**: Facilities managers won't understand "Persistence Window". | `Presence Verification Delay (seconds)`<br>*Helper text: Duration room must stay empty before starting shutdown timers.* |
| **L318** | `Empty Timeout (s)` | Slightly ambiguous. | `Unoccupied Auto-Off Delay (seconds)` |
| **L328** | `YOLO Confidence Threshold` | **ML Jargon**: Exposes ML model threshold parameters. | `Detection Sensitivity (0.1 - 1.0)`<br>*Helper text: Higher values reduce false detections from shadows.* |
| **L341** | `Device Shutdown Timeouts (s)` | Plain, but lacks guidance. | `Per-Device Auto-Off Delay (seconds)` |
| **L351** | `Headless Automation Mode (Disable Video Feed Stream)` | Direct, but can emphasize the privacy benefit. | `Headless Privacy Mode (Disable live video stream while keeping automatic controls active)` |
| **L356** | `Canvas Anonymization (Real-Time Face/Person Gaussian Blur)` | **Technical Term**: "Gaussian Blur" is unnecessary jargon. | `Blur People & Faces (Apply real-time blur to protect occupant privacy)` |
| **L361** | `Save Settings` | Generic button text. | `Save Configuration Changes` |

---

### 2.5 Facilities Reports & AI Forecasting

| Line Range | Original Copy | Weakness / Anti-Pattern | Rewritten Copy (Torrey & Joanna Standards) |
| :--- | :--- | :--- | :--- |
| **L387** | `Facilities Summary Report (CSV)` | Functional title. | `Facilities Energy & ROI Report (CSV)` |
| **L388** | `Download weekly energy savings, power draw & KPIs` | Good, but can be sharper. | `Export energy savings, power draw trends, and financial ROI data` |
| **L399** | `IoT Hardware Handoff Report (.md)` | Technical title. | `IoT Hardware Blueprint & Pinouts (.md)` |
| **L400** | `API payload schemas, ESP32 pinouts & relay specs` | Great technical summary. | `Download WebSocket schemas, ESP32 GPIO pinouts, and relay specifications` |
| **L421** | `Prometheus OpenMetrics Endpoint` | Clear for DevOps. | `Prometheus Live Metrics Endpoint` |
| **L422** | `Scrape live vision FPS, power draw & occupant gauges` | Good description. | `Stream live vision FPS, power draw, and occupant metrics to Grafana/Prometheus` |
| **L436** | `Target Hour Arrival Probability:` | Wordy label. | `Predicted Occupancy Likelihood:` |
| **L440** | `HVAC Pre-warm Action:` | Engineering terminology. | `HVAC Pre-Conditioning Status:` |

---

## 3. Section 2: CSV Reports & Facilities Notifications (`app/analytics/report_generator.py`)

### 3.1 Facilities CSV Report Evaluation & Rewrite

#### Current Output Defects:
1. **Aggressive Shouting Headers**: ALL CAPS title `VISION-BASED SMART ENERGY SAVING SYSTEM — FACILITIES SUMMARY REPORT` creates a harsh visual hierarchy in spreadsheet software.
2. **Raw ISO 8601 Timestamp**: `2026-08-09T17:36:34.123456` is difficult for building managers to quickly digest compared to formatted local timestamps.
3. **Cryptic Capitalization**: Column labels like `DEVICE ID` and `TARGET STATE` feel like database exports rather than executive reports.

---

## 4. Section 3: Jargon vs. Clarity Balance in Documentation

### 4.1 `README.md` Audit & Plain-Language Bridge

| Line Range | Technical Jargon in README | Recommended Plain-Language Rewrite |
| :--- | :--- | :--- |
| **L3** | `Centroid Multi-Object Tracking, Fast API for API routing...` | `YOLOv8 computer vision for occupant detection, persistent object tracking across temporary camera obstructions, and FastAPI for real-time control.` |
| **L9** | `integrated with CentroidTracker for persistent ID tracking across transient drops.` | `integrated with smart centroid tracking so people remain correctly counted even if briefly occluded or sitting still.` |
| **L11** | `Persistence Window (to absorb transient camera flickers)` | `Presence Verification Window (prevents lights from turning off if the camera briefly loses sight of an occupant).` |
| **L13** | `Real-time Energy ROI Analytics Engine` | `Real-Time Energy & Cost ROI Engine (tracks exact kWh saved, financial return, and carbon offset in real-time).` |

---

## 5. Section 4: Error Messages & Guidance for User Recovery

### 5.1 Standardized 3-Part Error Copy Formula

Every user-facing error message must follow Torrey Podmajersky's 3-part structure:
1. **What happened?** (Clear state explanation)
2. **Why it happened?** (Context without technical jargon)
3. **Actionable recovery** (What to do next)

#### Scenario 1: Zone Creation Failure (`saveNewZoneAndDevice`)
- **Header**: `Unable to Save Zone`  
- **Body**: `The system could not save your new spatial zone. Please check that all fields are filled correctly and the server connection is active.`  
- **Button Action**: `Try Again`

#### Scenario 2: Settings Update Failure (`saveConfig`)
- **Header**: `Settings Not Saved`  
- **Body**: `Your configuration changes could not be applied. Ensure the system server is online and values are within valid ranges.`  
- **Button Action**: `Review Settings`

---

## 6. Summary Checklist of Required Codebase Modifications

1. Update `app/static/index.html`:
   - Replace internal ML terms (`YOLO Person Count`, `Elapsed Zero Count`, `Persistence Window`).
   - Replace generic button texts (`Toggle` -> `Turn On` / `Turn Off`, `Reset Defaults` -> `Reset to Default Devices`).
   - Upgrade JS alert handling with human-centered error modal markup.
2. Update `app/analytics/report_generator.py`:
   - Format CSV headers to title case instead of shouting ALL CAPS.
   - Format timestamps to human-readable local dates.
3. Update `CONTEXT.md` & `README.md`:
   - Add plain-language translations next to technical concepts.
4. Update `docs/privacy.md`:
   - Strengthen trust copy and data privacy guarantees.
