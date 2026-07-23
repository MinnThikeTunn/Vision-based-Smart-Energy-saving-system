from dataclasses import dataclass
from enum import Enum


class RoomState(str, Enum):
    OCCUPIED = "Occupied"
    EMPTY = "Empty"


@dataclass
class OccupancySnapshot:
    state: RoomState
    occupant_count: int
    empty_duration_sec: float
    seconds_until_empty: float


class OccupancyStateMachine:
    def __init__(self, persistence_window_sec: float = 5.0, empty_timeout_sec: float = 180.0):
        self.persistence_window_sec = persistence_window_sec
        self.empty_timeout_sec = empty_timeout_sec

        self.current_state: RoomState = RoomState.EMPTY
        self.last_seen_time: float | None = None

    def update(self, raw_count: int, current_time: float) -> OccupancySnapshot:
        if raw_count > 0:
            self.current_state = RoomState.OCCUPIED
            self.last_seen_time = current_time
            return OccupancySnapshot(
                state=RoomState.OCCUPIED,
                occupant_count=raw_count,
                empty_duration_sec=0.0,
                seconds_until_empty=self.empty_timeout_sec,
            )

        # raw_count == 0
        if self.last_seen_time is None:
            self.current_state = RoomState.EMPTY
            return OccupancySnapshot(
                state=RoomState.EMPTY,
                occupant_count=0,
                empty_duration_sec=self.empty_timeout_sec,
                seconds_until_empty=0.0,
            )

        time_since_last_seen = current_time - self.last_seen_time

        if time_since_last_seen < self.persistence_window_sec:
            # Within persistence window -> maintain OCCUPIED state to absorb flicker
            self.current_state = RoomState.OCCUPIED
            return OccupancySnapshot(
                state=RoomState.OCCUPIED,
                occupant_count=0,
                empty_duration_sec=0.0,
                seconds_until_empty=self.empty_timeout_sec,
            )

        empty_elapsed = time_since_last_seen - self.persistence_window_sec
        if empty_elapsed >= self.empty_timeout_sec:
            self.current_state = RoomState.EMPTY

        remaining = max(0.0, self.empty_timeout_sec - empty_elapsed)
        return OccupancySnapshot(
            state=self.current_state,
            occupant_count=0,
            empty_duration_sec=empty_elapsed,
            seconds_until_empty=remaining,
        )
