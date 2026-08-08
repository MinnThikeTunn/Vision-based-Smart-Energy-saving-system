from app.decision_engine.device_matrix import DeviceControlMatrix
from app.decision_engine.state_machine import RoomState


def test_device_matrix_zone_b_only():
    matrix = DeviceControlMatrix(
        device_timeouts={"light": 5, "fan": 10, "ac": 10},
        zone_device_map={
            "Zone A (Desk)": ["light", "fan"],
            "Zone B (Transit)": ["ac"],
        },
    )

    current_states = {"light": "ON", "fan": "ON", "ac": "OFF"}

    # Occupant detected ONLY in Zone B (Transit)
    actions = matrix.evaluate(
        room_state=RoomState.OCCUPIED,
        empty_duration_sec=0.0,
        current_states=current_states,
        active_zones=["Zone B (Transit)"],
    )

    action_map = {a["device_id"]: a["action"] for a in actions}

    # AC should TURN_ON (since it's in Zone B)
    assert action_map.get("ac") == "TURN_ON"

    # Light and Fan should TURN_OFF (since Zone A is vacant)
    assert action_map.get("light") == "TURN_OFF"
    assert action_map.get("fan") == "TURN_OFF"
