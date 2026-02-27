from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable


@dataclass(slots=True)
class DomainEvent:
    name: str
    tenant_id: str
    payload: dict[str, Any]
    occurred_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None: ...

    @abstractmethod
    async def subscribe(self, event_name: str, handler: EventHandler) -> None: ...
