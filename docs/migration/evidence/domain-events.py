from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass(frozen=True, slots=True)
class DomainEvent:
    name: str
    tenant_id: str
    emitted_at: datetime


EVENT_TYPES: tuple[str, ...] = (
    "AgentInstalled",
    "ModelLoaded",
    "NodeJoined",
    "PolicyChanged",
    "TaskScheduled",
    "ResourceOverloaded",
    "PluginUpdated",
)


def new_event(name: str, tenant_id: str) -> DomainEvent:
    if name not in EVENT_TYPES:
        raise ValueError(f"unsupported event: {name}")
    return DomainEvent(name=name, tenant_id=tenant_id, emitted_at=datetime.now(UTC))
