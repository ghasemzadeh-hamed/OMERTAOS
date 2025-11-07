from __future__ import annotations

import datetime as dt
import io
import json
import os
from contextlib import closing
from typing import Any, Dict, List, Literal
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from minio import Minio
from pydantic import BaseModel

from app.control.app.routes.deps import get_clickhouse_client, get_pg_conn

router = APIRouter(prefix="/api/ingest/excel", tags=["ingest:excel"])


class ApplyMappingIn(BaseModel):
    tenant_id: str
    dataset_name: str
    mapping: Dict[str, str]
    options: Dict[str, Any] | None = None


class TriggerTrainIn(BaseModel):
    tenant_id: str
    dataset_id: str
    profile: Literal["lora", "ft_api"]
    budget_usd: float | None = None


def _infer_type(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "number"
    non_null = series.dropna()
    if not non_null.empty:
        try:
            matches = non_null.astype(str).str.match(r"^\d{4}-\d{2}-\d{2}")
            if matches.mean() > 0.6:
                return "date"
        except Exception:  # pragma: no cover - defensive
            pass
    return "string"


def _suggest_targets(column: str, dtype: str) -> List[str]:
    column_lc = column.lower()
    mapping_hints: Dict[str, List[str]] = {
        "customer_id": ["customer_id", "client_id", "cust_id"],
        "customer_name": ["customer_name", "name", "fullname"],
        "sku": ["sku", "product_code", "barcode"],
        "product_name": ["product_name", "item", "goods", "name"],
        "quantity": ["qty", "quantity", "count", "amount"],
        "unit_price": ["unit_price", "price", "rate"],
        "amount": ["amount", "total", "sum"],
        "currency": ["currency", "curr", "iso"],
        "invoice_no": ["invoice", "invoice_no", "factor", "order_no"],
        "order_date": ["order_date", "date", "created_at"],
        "ship_date": ["ship_date", "delivery_date"],
        "city": ["city", "town"],
        "region": ["region", "state", "province"],
        "notes": ["notes", "desc", "description", "memo"],
    }
    type_allow: Dict[str, set[str]] = {
        "number": {"quantity", "unit_price", "amount"},
        "date": {"order_date", "ship_date"},
        "string": {
            "customer_id",
            "customer_name",
            "sku",
            "product_name",
            "currency",
            "invoice_no",
            "city",
            "region",
            "notes",
        },
        "boolean": set(),
    }

    candidates: List[str] = []
    for target, hints in mapping_hints.items():
        if any(hint in column_lc for hint in hints):
            if not type_allow.get(dtype) or target in type_allow[dtype]:
                candidates.append(target)

    if not candidates:
        if dtype == "number":
            candidates.extend(["quantity", "unit_price", "amount"])
        elif dtype == "date":
            candidates.extend(["order_date", "ship_date"])

    seen: Dict[str, None] = {}
    return [seen.setdefault(item, None) or item for item in candidates if item not in seen][:3]


@router.post("/infer")
async def infer_schema(file: UploadFile = File(...), tenant_id: str = Form(...)) -> Dict[str, Any]:
    filename = file.filename or ""
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are accepted")

    payload = await file.read()
    try:
        dataframe = pd.read_excel(io.BytesIO(payload))
    except Exception as exc:  # pragma: no cover - pandas error path
        raise HTTPException(status_code=400, detail=f"Excel parse error: {exc}") from exc

    if dataframe.empty:
        raise HTTPException(status_code=400, detail="Excel has no rows")

    dataframe.columns = [str(column).strip() for column in dataframe.columns]
    inferred = {column: _infer_type(dataframe[column]) for column in dataframe.columns}
    sample_rows = dataframe.head(20).fillna("").to_dict(orient="records")
    suggestions = {column: _suggest_targets(column, inferred[column]) for column in dataframe.columns}

    return {
        "columns": list(dataframe.columns),
        "types": inferred,
        "sample": sample_rows,
        "suggestions": suggestions,
    }


@router.post("/apply-mapping")
async def apply_mapping(payload: ApplyMappingIn) -> Dict[str, Any]:
    mapped_columns = {source: target for source, target in payload.mapping.items() if target}
    if not mapped_columns:
        raise HTTPException(status_code=400, detail="At least one column must be mapped")

    client = get_clickhouse_client()
    type_map = {
        "customer_id": "String",
        "customer_name": "String",
        "sku": "String",
        "product_name": "String",
        "quantity": "Float64",
        "unit_price": "Float64",
        "amount": "Float64",
        "currency": "String",
        "invoice_no": "String",
        "order_date": "Date",
        "ship_date": "Date",
        "city": "String",
        "region": "String",
        "notes": "String",
    }
    with closing(get_pg_conn()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('dataset_catalog_dataset_id_seq')")
            dataset_id = cursor.fetchone()[0]

        table_name = f"aion_{payload.tenant_id}_{dataset_id}"
        column_defs = [f"`{target}` {type_map.get(target, 'String')}" for target in mapped_columns.values()]
        column_defs.append("ingested_at DateTime")
        client.command(
            f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)}) "
            "ENGINE = MergeTree ORDER BY ingested_at"
        )

        bucket = os.getenv("MINIO_BUCKET", "aion-processed")
        minio_client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
        )
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)

        commit_key = (
            f"processed/{payload.tenant_id}/{dataset_id}/"
            f"commit_{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
        )
        minio_client.put_object(
            bucket,
            commit_key,
            io.BytesIO(b"{}"),
            length=2,
            content_type="application/json",
        )

        storage_payload = json.dumps(
            {
                "minio_key": f"s3://{bucket}/{commit_key}",
                "clickhouse_table": table_name,
            }
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO dataset_catalog (dataset_id, tenant_id, dataset_name, mapping_json, storage_location)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    dataset_id,
                    payload.tenant_id,
                    payload.dataset_name,
                    json.dumps(mapped_columns),
                    storage_payload,
                ),
            )
        connection.commit()

    return {
        "dataset_id": str(dataset_id),
        "rows_committed": 0,
        "storage": {
            "minio_key": f"s3://{bucket}/{commit_key}",
            "clickhouse_table": table_name,
        },
        "catalog_entry": {
            "tenant_id": payload.tenant_id,
            "dataset_name": payload.dataset_name,
        },
    }


@router.post("/trigger-train")
async def trigger_train(payload: TriggerTrainIn) -> Dict[str, Any]:
    job_id = f"train-{uuid4()}"
    # In a full implementation this would enqueue a background task or orchestrator job.
    return {"job_id": job_id, "status": "queued"}

