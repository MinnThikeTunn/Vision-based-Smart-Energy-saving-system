from app.device_controller.simulation import SimulationController


def test_simulation_controller_initial_state():
    controller = SimulationController(latency_ms=0, power_ramp_sec=0)
    states = controller.get_device_states()
    assert states["light"] == "OFF"
    assert states["fan"] == "OFF"
    assert states["ac"] == "OFF"


def test_simulation_controller_toggle_and_logs():
    controller = SimulationController(latency_ms=0, power_ramp_sec=0)
    success = controller.set_device_state("light", "ON", reason="Manual override")
    assert success
    assert controller.get_device_states()["light"] == "ON"

    logs = controller.get_event_logs()
    assert len(logs) == 1
    assert logs[0]["device_id"] == "light"
    assert logs[0]["action"] == "ON"
    assert logs[0]["reason"] == "Manual override"
