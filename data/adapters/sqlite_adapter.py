from __future__ import annotations

import sqlite3
from typing import Any


class SQLiteAdapter:
    def __init__(self, dsn: str = ":memory:") -> None:
        self._conn = sqlite3.connect(dsn)

    def execute(self, query: str, params: dict[str, Any] | None = None) -> list[tuple[Any, ...]]:
        cur = self._conn.cursor()
        cur.execute(query, params or {})
        rows = cur.fetchall()
        self._conn.commit()
        return rows
