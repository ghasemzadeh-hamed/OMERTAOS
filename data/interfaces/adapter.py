from __future__ import annotations

from typing import Any, Protocol


class DatabaseAdapter(Protocol):
    def execute(self, query: str, params: dict[str, Any] | None = None) -> Any: ...


class AsyncDatabaseAdapter(Protocol):
    async def fetch_one(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None: ...

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int: ...
