"""Contract implemented by external telemetry exporters."""

from __future__ import annotations

from typing import Protocol


class TelemetryExporter(Protocol):
    async def publish(self, topic: str, payload: dict[str, object]) -> None: ...
