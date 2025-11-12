"""Process discovery capabilities."""

from collections import defaultdict
from typing import Dict, List, Set


class SimpleDiscoveryEngine:
    """Lightweight control-flow discovery inspired by Alpha/Heuristic Miner ideas."""

    def discover_relations(self, traces: Dict[str, List[str]]) -> Dict[str, Set[str]]:
        """Compute direct-follow relations for the provided traces."""
        follows: Dict[str, Set[str]] = defaultdict(set)
        for activities in traces.values():
            for idx in range(len(activities) - 1):
                current_activity = activities[idx]
                next_activity = activities[idx + 1]
                follows[current_activity].add(next_activity)
        return {activity: set(next_acts) for activity, next_acts in follows.items()}
