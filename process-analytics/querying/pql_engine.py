"""Simplified Process Query Language (PQL) engine."""

from typing import Dict, Iterable, List


class PQLEngine:
    """Evaluate lightweight PQL-like expressions over event traces."""

    def filter_cases(self, traces: Dict[str, List[str]], activity: str) -> List[str]:
        """Return case identifiers containing the specified activity."""
        return [case_id for case_id, acts in traces.items() if activity in acts]

    def frequency(self, traces: Dict[str, List[str]], activity: str) -> int:
        """Count how many times an activity appears across all traces."""
        return sum(acts.count(activity) for acts in traces.values())

    def sequence_exists(self, traces: Dict[str, List[str]], sequence: Iterable[str]) -> bool:
        """Check if the provided sequence appears in any trace."""
        seq = list(sequence)
        for acts in traces.values():
            if self._has_subsequence(acts, seq):
                return True
        return False

    @staticmethod
    def _has_subsequence(trace: List[str], sequence: List[str]) -> bool:
        if not sequence:
            return True
        seq_len = len(sequence)
        for idx in range(len(trace) - seq_len + 1):
            if trace[idx : idx + seq_len] == sequence:
                return True
        return False
