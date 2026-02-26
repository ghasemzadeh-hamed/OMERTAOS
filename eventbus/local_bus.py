from __future__ import annotations

import asyncio
from collections import defaultdict

from eventbus.interface import DomainEvent, EventBus, EventHandler


class LocalEventBus(EventBus):
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(event.name, []):
            asyncio.create_task(handler(event))

    async def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)
