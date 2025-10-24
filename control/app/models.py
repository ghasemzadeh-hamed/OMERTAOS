from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


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


@dataclass
class RouterDecision:
    route: str
    reason: str
    chosen_by: str = "policy"
    tier: str = "tier0"
