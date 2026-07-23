# 01 — Project Scaffold & System Configuration

**What to build:** Set up the application project structure, Python dependencies, central YAML settings configuration with Pydantic validation schema, and FastAPI REST endpoints to inspect and update runtime configuration.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Project scaffolding created according to recommended structure (`app/`, `config/`, `tests/`, `requirements.txt`).
- [ ] `settings.yaml` created with default parameters (camera settings, detector confidence, occupancy timeouts, device rules).
- [ ] Pydantic `SystemConfiguration` model validates loaded YAML settings.
- [ ] GET `/api/config` returns current system configuration.
- [ ] POST `/api/config` updates dynamic settings at runtime and validates changes.
- [ ] Unit test verifies configuration loading, default values, and schema validation.
