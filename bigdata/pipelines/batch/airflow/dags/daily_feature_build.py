"""Airflow DAG to build daily feature tables in MinIO."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "aionos",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_feature_build",
    description="Builds feature tables for routing decisions",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["aionos", "batch"],
) as dag:
    extract = BashOperator(
        task_id="extract_clickhouse",
        bash_command="python /opt/airflow/dags/scripts/extract_clickhouse.py",
    )

    transform = BashOperator(
        task_id="transform_features",
        bash_command="python /opt/airflow/dags/scripts/transform_features.py",
    )

    load = BashOperator(
        task_id="load_minio",
        bash_command="python /opt/airflow/dags/scripts/load_minio.py",
    )

    extract >> transform >> load
