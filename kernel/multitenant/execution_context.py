from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionContext:
    tenant_id: str
    capabilities: set[str] = field(default_factory=set)
    resource_limits: dict[str, Any] = field(default_factory=dict)
    policy_scope: str = "default"
