# 05 — React Dashboard Web UI

**What to build:** Develop a modern React/Vite single-page web dashboard displaying real-time video stream, telemetry cards, device controls, countdown timers, and event audit log table.

**Blocked by:** 04 — Device Control Layer & Real-Time Telemetry WebSocket

**Status:** ready-for-agent

- [ ] React/Vite dashboard scaffolded under `app/dashboard/` or root `frontend/`.
- [ ] Video stream component renders `/api/video_feed` MJPEG live camera feed.
- [ ] Telemetry header displays live occupant count badge, room occupancy status (`Occupied`/`Empty`), and uptime.
- [ ] Device control section displays virtual device cards (`Light`, `Fan`, `AC`) with active state badges, shutdown countdown timers, and manual simulation toggle switches.
- [ ] Event log table displays scrollable historical automation events.
- [ ] System settings panel allows viewing and editing dynamic configuration parameters via `/api/config`.
- [ ] End-to-end integration verified using simulation mode.
