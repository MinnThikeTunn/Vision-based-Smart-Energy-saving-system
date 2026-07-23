# Domain Glossary: Vision-Based Smart Energy Saving System

## Bounded Context: Occupancy & Energy Automation

### Terms

* **Occupant**: Detected person inside camera field of view.
* **Room Occupancy Status**: State of space (`Occupied` | `Empty`).
* **Empty Timeout**: Configurable duration without detected occupants before space transitions to `Empty`.
* **Persistence Window**: Buffer period (e.g., 5s of continuous zero detections) required before starting `Empty Timeout` to absorb transient detection flickers.
* **Occupancy State Machine**: State transitions between `Occupied` and `Empty`. `Occupied` transitions immediately on `raw_count > 0`. `Empty` requires `Persistence Window` + `Empty Timeout`.
* **Device Control Matrix**: Configurable per-device rule map defining ON/OFF conditions and independent shutdown timeouts for each device type (`Light`, `Fan`, `AC`).
* **Frame Queue**: Decoupled lock-free queue holding latest frame to separate high-rate video capture from inference processing.
* **Inference Worker**: Independent worker running object detection model on latest queued frame.
* **Control Mode**: Operating mode for energy control (`Simulation` | `IoT`). System defaults to `Simulation` using laptop camera & virtual device states, while defining abstract device controller interface for future IoT adapters.
* **MJPEG Stream**: Motion JPEG video stream (`/api/video_feed`) serving real-time webcam frames with rendered bounding boxes.
* **Status WebSocket**: Real-time bidirectional socket (`/ws/status`) broadcasting occupancy status, device states, timers, and event log updates.
* **System Configuration**: Schema-validated settings (`settings.yaml` / Pydantic model) specifying detection thresholds, camera parameters, timeouts, and device rules.
