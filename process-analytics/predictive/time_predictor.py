"""Predictive modeling for time-to-completion estimates."""

from statistics import mean
from typing import Dict, Iterable, List


class SimpleTimePredictor:
    """Estimate completion time based on historical durations."""

    def __init__(self):
        self.activity_duration_history: Dict[str, List[float]] = {}

    def update(self, activity: str, duration_ms: float) -> None:
        """Record an observed duration for the given activity."""
        self.activity_duration_history.setdefault(activity, []).append(duration_ms)

    def predict(self, remaining_activities: Iterable[str]) -> float:
        """Estimate time (ms) required to finish the remaining activities."""
        prediction = 0.0
        for activity in remaining_activities:
            history = self.activity_duration_history.get(activity)
            if not history:
                continue
            prediction += mean(history)
        return prediction
