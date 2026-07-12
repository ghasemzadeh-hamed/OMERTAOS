from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Protocol


class RuntimeTransportUnavailable(RuntimeError):
    """Raised when no versioned Runtime transport has been configured."""


@dataclass(frozen=True, slots=True)
class RuntimeEnvelope:
    tenant_id: str
    agent_id: str
    argv: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise ValueError("tenant_id is required")
        if not self.agent_id.strip():
            raise ValueError("agent_id is required")
        if not self.argv or any(not value for value in self.argv):
            raise ValueError("argv must contain non-empty arguments")


class RuntimeTransport(Protocol):
    async def execute(
        self,
        endpoint: str,
        envelope: RuntimeEnvelope,
        *,
        timeout_seconds: float,
    ) -> dict[str, object]: ...


class RuntimeDaemonClient:
    """Fail-closed facade for the versioned Control-to-Runtime transport."""

    def __init__(
        self,
        endpoint: str | None = None,
        *,
        transport: RuntimeTransport | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        resolved_endpoint = endpoint or os.getenv("AION_RUNTIME_ENDPOINT", "127.0.0.1:50051")
        if not resolved_endpoint.strip():
            raise ValueError("Runtime endpoint is required")
        if timeout_seconds <= 0:
            raise ValueError("Runtime timeout must be positive")
        self.endpoint = resolved_endpoint
        self._transport = transport
        self.timeout_seconds = timeout_seconds

    async def execute(self, envelope: RuntimeEnvelope) -> dict[str, object]:
        if self._transport is None:
            raise RuntimeTransportUnavailable(
                "Runtime transport is not configured; refusing to report synthetic success"
            )
        return await asyncio.wait_for(
            self._transport.execute(
                self.endpoint,
                envelope,
                timeout_seconds=self.timeout_seconds,
            ),
            timeout=self.timeout_seconds,
        )
