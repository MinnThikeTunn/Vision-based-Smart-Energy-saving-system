# 04 — Device Control Layer & Real-Time Telemetry WebSocket

**What to build:** Implement abstract device controller layer with `SimulationController` default implementation and bidirectional WebSocket endpoint broadcasting live telemetry and event logs to clients.

**Blocked by:** 03 — Occupancy State Machine & Device Decision Engine

**Status:** ready-for-agent

- [ ] `BaseDeviceController` interface defines `set_device_state(device_id, state)`.
- [ ] `SimulationController` manages virtual device states (`Light`, `Fan`, `AC`) and logs events to memory/file.
- [ ] WebSocket endpoint `/ws/status` pushes live telemetry (occupant count, occupancy status, device states, countdown timers, event logs) at 1-2 Hz.
- [ ] WebSocket client commands (manual simulation toggles) update device states and log events.
- [ ] Integration test verifies WebSocket connections, broadcast payload structure, and manual override command processing.
