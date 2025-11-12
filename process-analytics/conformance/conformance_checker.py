"""Conformance checking utilities."""

from typing import Dict, List, Set, Tuple


class ConformanceChecker:
    """Compare traces against allowed relations and detect deviations."""

    def __init__(self, allowed_relations: Dict[str, Set[str]]):
        self.allowed = allowed_relations

    def check_trace(self, case_id: str, activities: List[str]) -> List[Tuple[int, str, str]]:
        """Return a list of deviations (index, current activity, next activity)."""
        deviations: List[Tuple[int, str, str]] = []
        for idx in range(len(activities) - 1):
            current_activity = activities[idx]
            next_activity = activities[idx + 1]
            if next_activity not in self.allowed.get(current_activity, set()):
                deviations.append((idx, current_activity, next_activity))
        return deviations
