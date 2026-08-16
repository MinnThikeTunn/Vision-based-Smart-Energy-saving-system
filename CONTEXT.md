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
* **Time-Series Energy Snapshot**: 5-minute interval record capturing incremental delta kWh (baseline and actual), instantaneous power draw (Watts), active custom virtual devices, occupant count, and business operating schedule mask status.
* **24-Hour Energy Analytics Engine**: Aggregation module that compiles raw 5-minute interval snapshots into 24 hourly buckets (00:00–23:59) and daily summary metrics, preserving baseline schedule masking while accurately tracking off-schedule standby draw.
* **Cumulative Spatial Occupancy Heatmap**: 2D float32 spatial density matrix accumulating person footprint locations over time into spatial activity zones.
* **Footprint Center Splatting**: Gaussian kernel density distribution applied at bottom-center $(x_c, y_{max})$ of person bounding boxes to track floor position and dwell locations.
* **Fixed Absolute Density Scale**: Normalization of accumulated density against a fixed maximum threshold (person-seconds of presence) ensuring consistent color mapping across high and low activity sessions.
* **Multi-Channel Temporal Accumulator**: Parallel accumulator engine maintaining separate memory channels (`Instant ~10s`, `5-Minute Density`, `Session/Shift Density`) simultaneously in volatile RAM.
* **Zone Spatial Utilization Rate**: Percentage of a spatial zone's grid area exceeding baseline occupancy density thresholds.
* **Headless Spatial Heatmap Grid**: Synthetic dark grid background used in Headless Privacy Mode to visualize heatmap density without rendering raw camera video frames.
* **Hourly Heatmap Snapshot**: Periodically persisted PNG rendering of spatial density saved to storage for facility auditing and energy report export.
* **Inference Backend Cascade**: Dynamic runtime resolver that attempts hardware-accelerated runtimes (ONNX Runtime FP16) before falling back to PyTorch and DummyDetector.
* **Dynamic Time-of-Use (TOU) Tariff**: Structured multi-tier electricity pricing schedule assigning differentiated rates ($/kWh) across Peak, Mid-Peak, and Off-Peak hourly windows.
* **Camera Resilience Watchdog**: Non-blocking auto-reconnection loop monitoring video ingestion health and applying exponential backoff upon sensor disconnects without halting ASGI execution.
* **Pre-Allocated Zero-Copy Buffer Pool**: Static NumPy array containers reserved in volatile RAM across capture and frame transformation loops to eliminate dynamic garbage collector churn at 30 FPS.


