from __future__ import annotations

import os

import clickhouse_connect
import psycopg2

from ..config import get_settings


def _resolve_postgres_dsn() -> str:
    settings = get_settings()
    return os.getenv("POSTGRES_URL") or settings.postgres_dsn


def get_pg_conn() -> psycopg2.extensions.connection:
    """Return a synchronous PostgreSQL connection for catalog operations."""
    return psycopg2.connect(_resolve_postgres_dsn())


def get_clickhouse_client() -> clickhouse_connect.driver.client.Client:
    """Instantiate a ClickHouse client using environment overrides when present."""
    host = os.getenv("CLICKHOUSE_HOST", "clickhouse")
    port = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    username = os.getenv("CLICKHOUSE_USER", "default")
    password = os.getenv("CLICKHOUSE_PASSWORD", "")
    database = os.getenv("CLICKHOUSE_DATABASE", "default")
    return clickhouse_connect.get_client(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
    )
