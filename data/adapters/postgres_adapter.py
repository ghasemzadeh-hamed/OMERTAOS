from __future__ import annotations

from typing import Any


class PostgresAdapter:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def execute(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"dsn": self._dsn, "query": query, "params": params or {}}
