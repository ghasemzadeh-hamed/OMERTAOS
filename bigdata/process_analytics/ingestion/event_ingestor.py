"""Event ingestion utilities for process analytics."""

import datetime
from typing import Any, Dict

from ..core.utils import validate_event


class EventIngestor:
    """Normalize and validate events before writing them to a sink."""

    def __init__(self, sink):
        """Create a new ingestor with the provided sink."""
        self.sink = sink

    def ingest(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize the raw event, validate it, and persist via the sink."""
        event = self._normalize(raw_event)
        validate_event(event)
        self.sink.write(event)
        return event

    def _normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Map OMERTAOS event fields into the canonical schema."""
        return {
            "case_id": raw.get("case_id")
            or raw.get("task_id")
            or raw.get("session_id"),
            "activity": raw.get("activity") or raw.get("action"),
            "timestamp": raw.get("timestamp")
            or datetime.datetime.utcnow().isoformat(),
            "resource": raw.get("resource")
            or raw.get("agent_id")
            or raw.get("node"),
            "status": raw.get("status", "unknown"),
            "duration_ms": raw.get("duration_ms"),
            "attributes": raw.get("attributes", {}),
        }
