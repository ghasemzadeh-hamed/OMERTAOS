"""Synchronous in-process telemetry dispatch primitive."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable


TelemetryHandler = Callable[[dict[str, Any]], None]


class TelemetryBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[TelemetryHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: TelemetryHandler) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        for handler in self._handlers.get(event_name, []):
            handler(payload)
