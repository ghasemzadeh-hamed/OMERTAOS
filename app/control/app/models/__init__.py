from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Set


@dataclass
class StreamState:
    """In-memory book keeping for streaming control and acknowledgements."""

    cursor: str = "final"
    requires_ack: bool = True
    backpressure_hint: str | None = "wait-for-ack"
    retry_attempt: int = 0
    max_attempts: int = 3
    retry_after_ms: int = 0
    acked_by: Set[str] = field(default_factory=set)

    def mark_acked(self, consumer_id: str) -> None:
        self.acked_by.add(consumer_id)

    @property
    def acknowledged(self) -> bool:
        return bool(self.acked_by)


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    OK = "OK"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    CANCELED = "CANCELED"


@dataclass
class Task:
    schema_version: str
    task_id: str
    intent: str
    params: Dict[str, Any]
    preferred_engine: str
    priority: str
    sla: Dict[str, Any]
    metadata: Dict[str, Any]
    tenant_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    engine_route: Optional[str] = None
    engine_reason: Optional[str] = None
    engine_chosen_by: Optional[str] = None
    engine_tier: Optional[str] = None
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None
    usage: Dict[str, Any] = field(default_factory=dict)
    stream_state: StreamState = field(default_factory=StreamState)


@dataclass
class RouterDecision:
    route: str
    reason: str
    chosen_by: str = "policy"
    tier: str = "tier0"
