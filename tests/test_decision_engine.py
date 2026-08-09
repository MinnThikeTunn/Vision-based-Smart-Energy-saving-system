from app.decision_engine.device_matrix import DeviceControlMatrix
from app.decision_engine.state_machine import OccupancyStateMachine, RoomState


def test_occupancy_state_machine_occupied_instantly():
    sm = OccupancyStateMachine(persistence_window_sec=5, empty_timeout_sec=180)

    # Initial update with person present
    snapshot = sm.update(raw_count=2, current_time=100.0)
    assert snapshot.state == RoomState.OCCUPIED
    assert snapshot.occupant_count == 2


def test_persistence_window_flicker_absorption():
    sm = OccupancyStateMachine(persistence_window_sec=5, empty_timeout_sec=180)
    sm.update(raw_count=1, current_time=100.0)

    # 0 persons detected for 3 seconds (within 5s persistence window)
    snapshot = sm.update(raw_count=0, current_time=103.0)
    assert snapshot.state == RoomState.OCCUPIED  # Still occupied due to buffer!


def test_transition_to_empty():
    sm = OccupancyStateMachine(persistence_window_sec=5, empty_timeout_sec=180)
    sm.update(raw_count=1, current_time=100.0)

    # 0 persons detected past persistence (5s) + timeout (180s) = 185s total elapsed
    snapshot = sm.update(raw_count=0, current_time=286.0)
    assert snapshot.state == RoomState.EMPTY
    assert snapshot.empty_duration_sec >= 180.0


def test_device_control_matrix_rules():
    matrix = DeviceControlMatrix(device_timeouts={"light": 180, "fan": 600, "ac": 600})

    # Occupied state -> all devices ON
    actions = matrix.evaluate(
        room_state=RoomState.OCCUPIED,
        empty_duration_sec=0,
        current_states={"light": "OFF", "fan": "OFF", "ac": "OFF"},
    )
    action_dict = {a["device_id"]: a["action"] for a in actions}
    assert action_dict["light"] == "TURN_ON"
    assert action_dict["fan"] == "TURN_ON"
    assert action_dict["ac"] == "TURN_ON"

    # Empty for 200s -> Light OFF, Fan/AC remain ON
    actions_empty = matrix.evaluate(
        room_state=RoomState.EMPTY,
        empty_duration_sec=200,
        current_states={"light": "ON", "fan": "ON", "ac": "ON"},
    )
    empty_action_dict = {a["device_id"]: a["action"] for a in actions_empty}
    assert empty_action_dict.get("light") == "TURN_OFF"
    assert "fan" not in empty_action_dict  # Timeout (600s) not reached yet!


def test_decoupled_device_timeouts_during_occupied_empty_countdown():
    """Verify that devices with short shutdown timeouts turn OFF when empty_duration_sec reaches timeout, even if room state is OCCUPIED."""
    matrix = DeviceControlMatrix(device_timeouts={"light": 5, "fan": 10, "ac": 300})

    # Occupied room with 8 seconds empty duration (past 5s light timeout, but before 10s fan and 300s ac)
    actions = matrix.evaluate(
        room_state=RoomState.OCCUPIED,
        empty_duration_sec=8.0,
        current_states={"light": "ON", "fan": "ON", "ac": "ON"},
    )
    action_dict = {a["device_id"]: a["action"] for a in actions}

    assert action_dict.get("light") == "TURN_OFF"
    assert "fan" not in action_dict
    assert "ac" not in action_dict

