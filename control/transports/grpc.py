from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


class GrpcTransportUnavailable(RuntimeError):
    """Raised when the canonical generated gRPC server is not installed."""


ServerFactory = Callable[[str], Awaitable[None]]


@dataclass(slots=True)
class GrpcAdapter:
    endpoint: str
    server_factory: ServerFactory | None = None

    async def serve(self) -> None:
        if self.server_factory is None:
            raise GrpcTransportUnavailable(
                "Control gRPC server is not configured; refusing to start a no-op adapter"
            )
        await self.server_factory(self.endpoint)
