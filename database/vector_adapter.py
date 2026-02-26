from __future__ import annotations

from typing import Any

from data.vector.qdrant_client import get_qdrant_client


class VectorAdapter:
    def __init__(self) -> None:
        self._client = get_qdrant_client()

    def execute(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"query": query, "params": params or {}, "client": type(self._client).__name__}
