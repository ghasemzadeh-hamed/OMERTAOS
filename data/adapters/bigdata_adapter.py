from __future__ import annotations

from typing import Any, Protocol


class BigDataConnector(Protocol):
    def submit_job(self, payload: dict[str, Any]) -> str:
        ...
