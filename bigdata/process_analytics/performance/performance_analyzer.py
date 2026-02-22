"""Performance analytics helpers."""

import statistics
from typing import Any, Dict, List


class PerformanceAnalyzer:
    """Aggregate latency metrics for process activities."""

    def avg_activity_duration(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """Return the average duration per activity in milliseconds."""
        by_activity: Dict[str, List[float]] = {}
        for event in events:
            duration = event.get("duration_ms")
            if duration is None:
                continue
            activity = event["activity"]
            by_activity.setdefault(activity, []).append(float(duration))
        return {
            activity: statistics.mean(values)
            for activity, values in by_activity.items()
            if values
        }
