"""Airflow DAG to train router models weekly."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="weekly_model_train",
    description="Retrain routing policy model and publish to control plane",
    schedule_interval="0 5 * * 1",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["aionos", "ml"],
) as dag:
    train = BashOperator(
        task_id="train_model",
        bash_command="python /opt/airflow/dags/scripts/train_model.py",
    )

    upload = BashOperator(
        task_id="upload_model",
        bash_command="python /opt/airflow/dags/scripts/upload_model.py",
    )

    notify = BashOperator(
        task_id="notify_control",
        bash_command="curl -X POST http://control:8000/v1/router/policy/reload",
    )

    train >> upload >> notify
