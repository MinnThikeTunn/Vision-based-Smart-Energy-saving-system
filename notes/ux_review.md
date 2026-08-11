# Human-Centered Design & Usability Review: Vision Smart Energy v2

**Evaluator**: Don Norman (Human-Centered Design & Cognitive Ergonomics)  
**Target Codebase**: `D:\cvProject`  
**Artifacts Inspected**: [`app/static/index.html`](file:///D:/cvProject/app/static/index.html), [`README.md`](file:///D:/cvProject/README.md), [`docs/privacy.md`](file:///D:/cvProject/docs/privacy.md)  
**Date**: August 9, 2026  

---

## Executive Summary: The Conceptual Model Gap

The Vision Smart Energy v2 system exhibits high visual aesthetic quality (dark mode styling, glassmorphism, responsive typography), but suffers from fundamental **Human-Centered Design (HCD) breakdowns**. 

The system exposes its internal engineering implementation (YOLO object detection, Pydantic configuration fields, WebSocket payloads, normalized bounding boxes) directly onto the user interface. This creates a severe **Gulf of Execution** and **Gulf of Evaluation** for both facility managers and room occupants.

---

## 1. Dashboard Cognitive Load & Information Hierarchy

### 1.1 Artificial Bifurcation (Split-Attention Effect)
* **The Flaw**: The UI splits core operations across two distinct pages ("Live Control Center" and "Settings & Analytics Hub").
* **Impact**: Facility managers configuring device shutdown timers on Page 2 must switch back to Page 1 to observe the live effect on device countdowns (`timer-light`, `timer-fan`, `timer-ac`). This forces high working-memory retention across page transitions.
* **Violation**: Principle of Spatial Contiguity & Proximity. Controls and their direct feedback loops must exist within the same visual boundary.

### 1.2 Engineering Jargon Overload
* **The Flaw**: Technical terms from the computer vision pipeline are displayed verbatim:
  * `"YOLO Person Count"`
  * `"Elapsed Zero Count"`
  * `"YOLO Confidence Threshold"`
  * `"Persistence Window (s)"`
* **Impact**: A facilities manager or occupant does not care about "YOLO confidence thresholds" or "Elapsed Zero Count". They need operational terms: *"Detection Sensitivity"*, *"Flicker Delay"*, and *"Time Room Has Been Vacant"*.
* **Violation**: Match Between System and the Real World (User Language vs. Computer Language).

### 1.3 Cluttered Telemetry Hierarchy
* **The Flaw**: Page 1 displays 4 primary telemetry cards (*Occupants*, *Room Status*, *Empty Duration*, *Room Countdown*) alongside sub-timers (*Light*, *Fan*, *AC*). Page 2 introduces 4 additional telemetry cards (*Live Power Draw*, *Cumulative Saved*, *Financial Saved*, *Efficiency Gain*), a Chart.js line graph, a settings form, facilities export links, and an AI forecast card.
* **Impact**: Information density is distributed evenly without visual accentuation for critical state changes (e.g., an impending automatic power-down).

---

## 2. Visual Affordances & Signifiers

### 2.1 Ambiguous Device Controls
* **The Flaw**: Devices are toggled via generic text buttons: `<button onclick="toggleDevice('${dev}')">Toggle</button>`.
* **Impact**: The button reads "Toggle" regardless of whether the device state is `ON`, `OFF`, or `DIM`. The button lacks a physical affordance (such as a standard toggle switch knob or explicit binary color indicator on the trigger itself). The user must read adjacent text (`State: ON (100%)`) to infer state.
* **Violation**: Signifiers must explicitly indicate *what action will happen* before the action is taken.

### 2.2 Zone Spatial Mapping Disconnect
* **The Flaw**: Zone creation relies on clicking `+ Draw Zone & Add Device`, which opens a canvas overlay on top of the live video stream.
* **Impact**:
  1. Once drawing starts, there is no on-screen affordance or visual banner informing the user: *"Click and drag on the camera feed to outline a spatial zone."*
  2. Bounding boxes drawn on the video feed are saved as raw normalized coordinates (`[x_min, y_min, x_max, y_max]`).
  3. Crucially, the right-hand device cards (`#device-list-container`) **do not indicate which spatial zone they are bound to**. Spatial mapping is completely disconnected between the 2D video feed and the device list.
* **Violation**: Principle of Natural Mapping. The spatial relationship between physical room controls, video regions, and virtual switches is invisible.

### 2.3 Headless Privacy Mode Feedback Vacuum
* **The Flaw**: Headless Privacy Mode (`privacy.headless_mode`) is toggled via a checkbox inside the Page 2 Settings tab.
* **Impact**: When Headless Mode is activated (disabling `/api/video_feed`), the Live Control Center on Page 1 shows a black/broken image container with zero feedback. There is no visual privacy badge or overlay stating: *"Privacy Mode Active — Camera Feed Hardware-Disabled"*.
* **Violation**: Feedback & Perceived System State. Users cannot distinguish between a broken camera/network error and intentional privacy-first headless operation.

---

## 3. Error Prevention, System State Feedback & Recovery

### 3.1 Silent Failures on WebSocket Disconnect
* **The Flaw**: When WebSocket connectivity drops, `toggleDevice()` silently aborts execution:
  ```javascript
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ```
* **Impact**: Clicking a device button while disconnected results in zero visual feedback, zero error toast, and no retry attempt. The user assumes the system is unresponsive.
* **Violation**: Error Feedback & Forgiving Infrastructure.

### 3.2 Destructive Action Without Safety Guardrails
* **The Flaw**: The "Reset Defaults" button on the Virtual Devices card triggers `resetToDefaultDevices()` directly without a confirmation dialog or undo mechanism.
* **Impact**: A single accidental click permanently wipes out all custom spatial zones and user-configured devices from system state.
* **Violation**: Defensive Design & Slips/Mistakes Prevention.

### 3.3 Intrusive Modal Dialog Feedback
* **The Flaw**: Configuration saves and zone creations trigger browser-native `alert()` boxes (e.g., `alert("Settings updated successfully!")`).
* **Impact**: Native `alert()` dialogs freeze the main UI thread, break user momentum, and represent obsolete interaction patterns.
* **Violation**: Seamless Non-Blocking Feedback (Toasts / Status Badges).

### 3.4 State Machine Timer Ambiguity
* **The Flaw**: The relationship between *Persistence Window* (e.g., 3s debounce), *Empty Timeout* (e.g., 5s grace period), and individual *Device Shutdown Timeouts* is unexplained in the UI.
* **Impact**: Users cannot predict *when* a specific appliance will turn off upon room exit because the multi-stage countdown logic is hidden inside backend code (`state_machine.py`).

---

## 4. Self-Sufficiency Benchmark (No-Documentation Test)

| User Persona | Can They Succeed Without Docs? | Key Blocker |
| :--- | :---: | :--- |
| **Facilities Manager** | **NO** | Needs to translate CV terminology (*YOLO Confidence*, *Persistence Window*) into facilities management parameters; cannot correlate device cards with spatial zones. |
| **Room Occupant** | **NO** | Cannot verify whether camera feeds are recording/streaming; privacy controls are buried in secondary settings; cannot tell why devices auto-power down. |

---

## 5. Actionable HCD Remediation Roadmap

1. **Unify Operational Dashboard (Eliminate Split-Attention)**
   * Move device shutdown timeouts and privacy toggles into an inline collapsible drawer on Page 1. Keep live countdown feedback adjacent to configuration inputs.
2. **Replace Jargon with User Mental Models**
   * Rename `YOLO Confidence` $\rightarrow$ `Detection Sensitivity`.
   * Rename `Persistence Window` $\rightarrow$ `Flicker Protection Buffer`.
   * Rename `Elapsed Zero Count` $\rightarrow$ `Time Vacant`.
3. **Upgrade Device Toggles & Signifiers**
   * Replace `<button>Toggle</button>` with standard UI toggle switches that display distinct visual states (`ON` [Emerald], `OFF` [Zinc/Dark], `DIM` [Amber]).
4. **Fix Zone-to-Device Spatial Mapping**
   * Display zone badges directly on device cards (e.g., `Desk Lamp [Zone A: Workstation 1]`).
   * Highlight corresponding bounding boxes on video feed when hovering over a device card.
5. **Implement Explicit Headless Privacy Signifiers**
   * When video stream is disabled via Headless Mode, display a prominent shield overlay on the video container: *"🔒 Headless Privacy Mode Enabled — Zero Video Streaming"*.
6. **Implement Non-Blocking Toast System & Defensive Confirmations**
   * Replace native `alert()` dialogs with non-intrusive status toasts.
   * Add a modal confirmation guardrail to "Reset Defaults".
   * Show an inline warning toast when user attempts to click controls during WebSocket disconnect.

---
*End of UX Review.*
