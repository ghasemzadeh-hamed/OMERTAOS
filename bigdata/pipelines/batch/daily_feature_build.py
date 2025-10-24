"""Airflow DAG building router training features every day (dev: every 5 minutes)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import dag, task
from airflow.providers.http.hooks.http import HttpHook

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
FEATURE_PATH = os.getenv("FEATURE_PATH", "s3a://aion-features/router/")
CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "http://clickhouse:8123")


def _default_args() -> dict:
    return {
        "owner": "aion",
        "depends_on_past": False,
        "email_on_failure": True,
        "email": [os.getenv("ALERT_EMAIL", "dataops@example.com")],
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }


@dag(
    schedule=timedelta(minutes=int(os.getenv("FEATURE_BUILD_INTERVAL_MINUTES", "5"))),
    start_date=datetime(2024, 3, 1),
    catchup=False,
    default_args=_default_args(),
    tags=["router", "features"],
)
def daily_feature_build() -> None:
    @task()
    def extract_signals() -> dict:
        # Placeholder query logic. Replace with real ClickHouse SQL client.
        query = {
            "sql": "SELECT * FROM aion.decisions WHERE ts_event >= now() - INTERVAL 7 DAY",
        }
        return query

    @task()
    def transform(payload: dict) -> dict:
        # Combine decisions, tasks, metrics (stub logic)
        return {
            "feature_table": "router_features",
            "columns": [
                "task_id",
                "latency_budget",
                "cost_budget",
                "data_size",
                "privacy_level",
                "historical_success_rate",
                "model_load",
                "time_of_day",
            ],
            "path": f"{FEATURE_PATH}{datetime.utcnow():%Y/%m/%d}/router_features.parquet",
        }

    @task()
    def load(features: dict) -> str:
        # Write metadata entry into the MinIO catalog (stub)
        return json.dumps(features)

    load(transform(extract_signals()))


daily_feature_build_dag = daily_feature_build()
