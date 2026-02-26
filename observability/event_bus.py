from __future__ import annotations

from typing import Protocol


class EventBus(Protocol):
    async def publish(self, topic: str, payload: dict[str, object]) -> None: ...
