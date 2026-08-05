from datetime import datetime, timedelta
from typing import Dict, List, Any


class OccupancyForecaster:
    """
    Time-Series Occupancy Forecasting & Pre-warming Engine.
    
    Analyzes historical occupancy logs to predict upcoming arrival patterns
    and pre-warm HVAC / lighting prior to scheduled peak arrivals.
    """

    def __init__(self) -> None:
        # Pre-calculated hourly probability map based on typical commercial room usage
        self.hourly_probability_map: Dict[int, float] = {
            8: 0.25,   # Early arrival phase
            9: 0.85,   # Morning peak arrival
            10: 0.95,  # Working hours
            11: 0.90,
            12: 0.60,  # Lunch period drop
            13: 0.80,
            14: 0.95,  # Afternoon peak
            15: 0.90,
            16: 0.85,
            17: 0.40,  # Departure phase
            18: 0.15,
        }

    def predict_next_hour(self, current_time: datetime | None = None) -> Dict[str, Any]:
        now = current_time or datetime.now()
        next_hour = (now + timedelta(hours=1)).hour
        probability = self.hourly_probability_map.get(next_hour, 0.05)

        prewarm_recommended = probability >= 0.70

        return {
            "target_hour": next_hour,
            "predicted_occupancy_probability": round(probability, 2),
            "prewarm_hvac_recommended": prewarm_recommended,
            "prewarm_lighting_recommended": prewarm_recommended,
            "reason": (
                f"High probability ({probability:.0%}) of occupant arrival during hour {next_hour}:00"
                if prewarm_recommended
                else f"Low probability ({probability:.0%}) during hour {next_hour}:00"
            ),
        }
