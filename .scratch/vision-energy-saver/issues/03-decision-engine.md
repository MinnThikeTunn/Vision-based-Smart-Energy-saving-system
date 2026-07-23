# 03 — Occupancy State Machine & Device Decision Engine

**What to build:** Implement the core 2-tiered occupancy state machine and rule-based device decision engine to calculate room occupancy status and trigger automated device state changes.

**Blocked by:** 02 — Vision Pipeline & Decoupled Inference Worker

**Status:** ready-for-agent

- [ ] `OccupancyStateMachine` manages room state (`Occupied` vs `Empty`).
- [ ] `raw_count > 0` instantly sets room state to `Occupied` and clears shutdown timers.
- [ ] `raw_count == 0` triggers 5-second `Persistence Window` buffer before initiating `Empty Timeout` countdown.
- [ ] `DeviceControlMatrix` applies per-device rules (Light: 3 min timeout, Fan/AC: 10 min timeout).
- [ ] State transitions generate structured automation events.
- [ ] Unit tests verify persistence window flicker absorption, state transitions, and per-device shutdown countdown calculation using synthetic detection sequences.
