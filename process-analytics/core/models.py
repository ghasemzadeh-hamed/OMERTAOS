"""Core data models for the process analytics module."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ProcessEvent:
    """Normalized representation of an OMERTAOS event."""

    case_id: str
    activity: str
    timestamp: datetime
    resource: Optional[str] = None
    status: str = "unknown"
    duration_ms: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSnapshot:
    """Collection of process metrics captured at a point in time."""

    timestamp: datetime
    values: Dict[str, float]
