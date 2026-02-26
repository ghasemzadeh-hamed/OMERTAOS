from __future__ import annotations

from dataclasses import dataclass

@dataclass(slots=True)
class GrpcAdapter:
    endpoint: str

    async def serve(self) -> None:
        return None
