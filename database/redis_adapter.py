from __future__ import annotations

from typing import Any


class RedisAdapter:
    def __init__(self, url: str) -> None:
        self._url = url

    def execute(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"url": self._url, "command": query, "params": params or {}}
