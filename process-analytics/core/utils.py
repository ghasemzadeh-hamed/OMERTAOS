"""Utility helpers for the process analytics module."""

from typing import Any, Dict, List

REQUIRED_FIELDS = {"case_id", "activity", "timestamp"}


def validate_event(event: Dict[str, Any]) -> None:
    """Validate that the event dictionary conforms to the required schema."""
    missing = REQUIRED_FIELDS.difference(event)
    if missing:
        raise ValueError(f"Event missing required fields: {sorted(missing)}")


class InMemoryEventSink:
    """Simple in-memory sink useful for prototyping and tests."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def write(self, event: Dict[str, Any]) -> None:
        self.events.append(event)

    def list_events(self) -> List[Dict[str, Any]]:
        return list(self.events)
