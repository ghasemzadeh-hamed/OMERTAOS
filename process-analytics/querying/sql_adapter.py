"""SQL adapter for process data stores."""

from typing import Any, Iterable


class SQLAdapter:
    """Execute SQL queries using a provided database connector."""

    def __init__(self, connector):
        self.connector = connector

    def execute(self, query: str, params: Iterable[Any] | None = None):
        """Run the SQL query through the connector and return the result."""
        cursor = self.connector.cursor()
        cursor.execute(query, tuple(params or ()))
        return cursor.fetchall()
