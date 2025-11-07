"""Model management endpoints."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from .security import admin_or_devops_required, admin_required


router = APIRouter(prefix="/api/models", tags=["models"])

MODELS_DIR = Path(os.getenv("AION_CONTROL_MODELS_DIRECTORY", "./models")).expanduser()
MODELS_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_PATH = Path(os.getenv("AION_MODEL_REGISTRY", "config/model-registry.json"))


def _load_registry() -> list[dict[str, Any]]:
    if not REGISTRY_PATH.exists():
        return []
    import json

    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "models" in data:
        return list(data["models"])
    return []


def _list_local_models() -> list[dict[str, Any]]:
    items = []
    for path in MODELS_DIR.glob("**/*"):
        if path.is_file():
            stat = path.stat()
            items.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "size": stat.st_size,
                    "modified_at": stat.st_mtime,
                }
            )
    return items


@router.get("")
async def list_models(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    return {
        "local": _list_local_models(),
        "registry": _load_registry(),
    }


async def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
        response = await client.get(url)
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="download failed")
        destination.write_bytes(response.content)


@router.post("/install")
async def install_model(
    payload: dict[str, Any],
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    name = payload.get("name")
    source = payload.get("source")
    url = payload.get("url")
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name required")
    target = MODELS_DIR / name
    if source == "url":
        if not url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="url required")
        await _download(url, target)
    elif source == "registry":
        registry = {entry.get("name"): entry for entry in _load_registry()}
        if name not in registry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="model not in registry")
        entry = registry[name]
        entry_url = entry.get("url")
        if not entry_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="registry entry missing url")
        await _download(entry_url, target)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported source")
    return {"ok": True, "path": str(target)}


@router.post("/remove")
async def remove_model(
    payload: dict[str, Any],
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name required")
    target = MODELS_DIR / name
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="model not found")
    target.unlink()
    return {"ok": True}


__all__ = ["router"]
