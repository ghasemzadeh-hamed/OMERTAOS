"""Dataset registry endpoints."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from .security import admin_or_devops_required, admin_required


router = APIRouter(prefix="/api/datasets", tags=["datasets"])

DATASET_REGISTRY = Path(os.getenv("AION_DATASET_REGISTRY", "config/datasets.json"))


def _load_registry() -> list[dict[str, Any]]:
    if not DATASET_REGISTRY.exists():
        return []
    data = json.loads(DATASET_REGISTRY.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("datasets", []) if isinstance(data, dict) else []


def _write_registry(entries: list[dict[str, Any]]) -> None:
    DATASET_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    DATASET_REGISTRY.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")


@router.get("")
async def list_datasets(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    return {"datasets": _load_registry()}


@router.post("/register")
async def register_dataset(
    payload: dict[str, Any],
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    name = payload.get("name")
    path = payload.get("path")
    dtype = payload.get("type")
    if not name or not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name and path required")
    entries = _load_registry()
    entry = {
        "name": name,
        "path": path,
        "type": dtype or "unknown",
        "registered_at": datetime.utcnow().isoformat() + "Z",
        "status": "registered",
    }
    entries = [item for item in entries if item.get("name") != name]
    entries.append(entry)
    _write_registry(entries)
    return {"ok": True, "dataset": entry}


@router.post("/delete")
async def delete_dataset(
    payload: dict[str, Any],
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name required")
    entries = _load_registry()
    entries = [item for item in entries if item.get("name") != name]
    _write_registry(entries)
    return {"ok": True}


__all__ = ["router"]
