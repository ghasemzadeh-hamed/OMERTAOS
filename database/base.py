from __future__ import annotations

from typing import Any, Protocol


class DatabaseAdapter(Protocol):
    def execute(self, query: str, params: dict[str, Any] | None = None) -> Any:
        ...
