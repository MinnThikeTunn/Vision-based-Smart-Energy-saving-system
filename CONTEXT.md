# Domain Glossary: Vision-Based Smart Energy Saving System

## Bounded Context: Occupancy & Energy Automation

### Core Terms & Domain Concepts

* **Occupant**: Detected person inside camera field of view.
* **Room Occupancy Status**: Real-time operational state of space (`Occupied` | `Empty`).
* **Unoccupied Auto-Off Delay (formerly Empty Timeout)**: Configurable duration without detected occupants before space transitions to `Empty` and macro shutdown actions initiate.
* **Presence Verification Delay (formerly Persistence Window)**: Required continuous buffer period (e.g., 2s of zero detections) before confirming space is empty, absorbing transient detection flickers or brief camera obstructions.
* **Occupancy State Machine**: State engine managing transitions between `Occupied` and `Empty`. `Occupied` transitions immediately on `occupant_count > 0`. `Empty` requires `Presence Verification Delay` + `Unoccupied Auto-Off Delay`.
* **Decoupled Device Control Matrix**: Configurable per-device rule map defining independent shutdown delays and power levels for each device type (`Light`, `Fan`, `AC`). Devices in vacant spatial zones start independent countdown timers immediately after `Presence Verification Delay`.
* **Net Saved Energy Formula**: Audit-ready ROI calculation subtracting edge compute server power overhead: $\text{Net Saved kWh} = \text{Baseline Appliance kWh} - \text{Actual Appliance kWh} - \text{Edge Compute Overhead kWh}$.
* **Edge Compute Overhead**: Continuous power draw (e.g. 30W) consumed by local GPU/CPU hardware running video inference pipeline 24/7.
* **Business Operating Schedule**: Configurable operational window mask (e.g., 08:00 to 19:00 Mon–Fri) during which baseline energy accumulation occurs. Prevents accumulating baseline savings when buildings are scheduled empty overnight.
* **Frame Queue**: Lock-free single-element buffer holding latest frame to decouple high-rate camera capture from inference processing.
* **Inference Worker**: Independent worker thread executing YOLOv8 person detection on latest queued frame.
* **Headless Privacy Mode**: Operating mode that runs video analytics in volatile memory without streaming or displaying raw camera frames.
* **MJPEG Stream**: Motion JPEG video stream (`/api/video_feed`) serving real-time webcam frames with rendered bounding boxes.
* **Status WebSocket**: Real-time bidirectional socket (`/ws/status`) broadcasting occupancy status, device states, timers, and event log updates.
* **Custom Virtual Device**: User-defined virtual electrical appliance entity characterized by a unique identifier, category/icon (Light, Fan, HVAC, Electronics, Custom), rated power draw (Watts), unoccupied shutdown delay (seconds), and optional per-device power ramp profile duration (seconds).
* **Zero-Device Onboarding State**: Initial default system state when zero devices and zero spatial zones are configured. Baseline power accumulation remains idle (0 W) and the UI side panel presents an interactive 2-step setup wizard guiding device and zone creation.
* **Room-Wide (Global) Device**: Custom virtual device that is not assigned to a specific spatial bounding box; its shutdown state machine is driven by overall room occupancy.

