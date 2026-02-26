from __future__ import annotations

from typing import Protocol, Any


class DatabaseAdapter(Protocol):
    async def fetch_one(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None: ...
    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int: ...
