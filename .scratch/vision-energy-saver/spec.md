# Spec: Vision-Based Smart Energy Saving System

## Problem Statement

Traditional motion sensors (PIR) and fixed timers frequently cause false energy shutdowns when occupants are sitting still, or keep devices powered on in empty rooms. Manual energy management is error-prone, leading to unnecessary electrical costs and energy waste in homes and office spaces.

## Solution

A vision-based smart energy-saving application that processes live webcam feeds using YOLOv8 person detection to accurately identify room occupancy. It uses a 2-tiered state machine with a persistence buffer window and configurable per-device shutdown timeouts to intelligently control virtual or IoT-connected electrical devices (lights, fans, AC), avoiding rapid switching and false shutdowns while maximizing energy efficiency.

## User Stories

1. As a facility manager, I want the system to continuously capture live video from my laptop/webcam, so that room occupancy is monitored in real time.
2. As a facility manager, I want the system to detect and count occupants in real time using YOLOv8, so that occupancy estimates are accurate regardless of physical movement.
3. As an occupant, I want short postural shifts or occlusions to be buffered by a persistence window (5s), so that the lights and AC do not turn off unexpectedly while I am sitting still.
4. As a facility manager, I want room status to transition to `Empty` only after continuous zero detections for a configurable `empty_timeout` (e.g. 180s), so that devices remain powered during brief absences.
5. As an environmental officer, I want individual shutdown timeouts for different device types (e.g., Light after 3 min, Fan/AC after 10 min), so that energy-intensive appliances are managed according to their usage patterns.
6. As a system administrator, I want to operate the system initially in `Simulation` mode, so that device states and events are accurately visualized without requiring physical IoT hardware.
7. As an IoT engineer, I want an abstract `BaseDeviceController` interface, so that future IoT communication modules (ESP32/MQTT/HTTP Relays) can be plugged in without refactoring the decision engine.
8. As a user, I want a live Dashboard displaying the camera feed with bounding boxes and occupant count, so that I can visually verify system performance.
9. As an operator, I want real-time WebSocket updates on occupant count, occupancy status (`Occupied`/`Empty`), active device states, and shutdown countdown timers on the Dashboard, so that I have complete operational awareness.
10. As an operator, I want an event log table on the Dashboard, so that I can audit historical state changes and automated device commands.
11. As an operator, I want to update system configuration (camera index, confidence threshold, timeouts, device rules) via a REST API or UI panel, so that parameters can be tuned dynamically.
12. As a system administrator, I want non-blocking multi-threaded processing between frame capture and YOLO inference, so that the camera video stream remains fluid (15-30 FPS) even under heavy model computation.

## Implementation Decisions

- **Domain Model & Glossary Alignment**: Use `CONTEXT.md` terminology (`Occupant`, `Room Occupancy Status`, `Empty Timeout`, `Persistence Window`, `Occupancy State Machine`, `Device Control Matrix`, `Frame Queue`, `Inference Worker`, `Control Mode`, `MJPEG Stream`, `Status WebSocket`, `System Configuration`).
- **Decoupled Video Pipeline**: Camera capture thread reads OpenCV webcam frames into a single-item lock-free queue (`Frame Queue`). `Inference Worker` thread consumes the latest available frame, runs YOLOv8 model (`yolov8n.pt`), updates `raw_count` and detection overlays.
- **State Machine & Rule Engine**:
  - `OccupancyStateMachine` manages state (`Occupied` | `Empty`).
  - `raw_count > 0` instantly sets state to `Occupied` and resets timers.
  - `raw_count == 0` enters `Persistence Window` (5s); if zero count persists throughout, `Empty Timeout` countdown begins.
  - `DeviceControlMatrix` evaluates per-device timeouts (e.g., Light: 180s, Fan/AC: 600s) and triggers device state commands upon expiration.
- **Backend Architecture**: FastAPI application providing:
  - GET `/api/video_feed`: MJPEG stream with overlay bounding boxes.
  - WS `/ws/status`: Bidirectional WebSocket pushing state updates, device statuses, countdowns, and logs at 1-2 Hz.
  - GET/POST `/api/config`: REST endpoints to inspect and update runtime configuration validated via Pydantic schemas.
- **Device Control Layer**:
  - `BaseDeviceController` abstract class with `set_device_state(device_id, state)`.
  - `SimulationController` (default) maintaining in-memory device states (`ON`/`OFF`) and emitting formatted event log entries.
  - Future `IoTController` stub for HTTP/MQTT relay commands.
- **Frontend Dashboard**: Single-page React/Vite app displaying live video stream, status widgets (occupant count, occupancy badge, countdown timers), device control cards (with simulation manual override controls), and scrollable event logs.

## Testing Decisions

- **Testing Philosophy**: Test external behavior through public APIs and domain state transitions, not internal thread loops or private helpers.
- **Seam 1: API / System Seam**: FastHTTP test client testing REST endpoints (`/api/config`) and WebSocket connections (`/ws/status`). Simulated frame injection to verify status broadcast payloads and MJPEG feed responses.
- **Seam 2: Decision Engine Seam**: Unit/integration tests driving `OccupancyStateMachine` and `DeviceControlMatrix` with deterministic frame count series (`[1, 1, 0, 0, 0...]`) and mock time ticks to test `Persistence Window` handling, timeout countdowns, and device ON/OFF command generation.

## Out of Scope

- Facial recognition / identity tracking of specific individuals.
- Complex activity recognition (e.g., studying vs sleeping).
- Cloud synchronization and multi-camera cluster management.
- Hardware PCB layout / ESP32 firmware flashing.

## Further Notes

- Architecture strictly follows ADR 0001 (Decoupled Capture and Inference).
- Default execution stack uses laptop webcam (camera index `0`) and simulated hardware outputs.
