from __future__ import annotations

from typing import Any


class MongoAdapter:
    def __init__(self, uri: str) -> None:
        self._uri = uri

    def execute(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"uri": self._uri, "query": query, "params": params or {}}
