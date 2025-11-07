"""Plugin package manager endpoints."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from .security import admin_or_devops_required, admin_required


router = APIRouter(prefix="/api/packages", tags=["packages"])

REGISTRY_FILE = Path(os.getenv("AION_PACKAGE_REGISTRY", "config/packages/registry.json"))
INSTALL_STATE = Path(os.getenv("AION_PACKAGE_STATE", "config/packages/installed.json"))


def _load_registry() -> list[dict[str, Any]]:
    if not REGISTRY_FILE.exists():
        return []
    data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("packages", []) if isinstance(data, dict) else []


def _load_state() -> dict[str, Any]:
    if not INSTALL_STATE.exists():
        return {"installed": []}
    return json.loads(INSTALL_STATE.read_text(encoding="utf-8"))


def _write_state(state: dict[str, Any]) -> None:
    INSTALL_STATE.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_STATE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


@router.get("")
async def list_packages(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    state = _load_state()
    registry = _load_registry()
    installed = {pkg["name"] for pkg in state.get("installed", [])}
    for entry in registry:
        entry["installed"] = entry.get("name") in installed
    return {"registry": registry, "installed": state.get("installed", [])}


@router.post("/install")
async def install_package(
    payload: dict[str, Any],
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name required")
    registry = {entry.get("name"): entry for entry in _load_registry()}
    if name not in registry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="package not found")
    state = _load_state()
    installed = [pkg for pkg in state.get("installed", []) if pkg.get("name") != name]
    entry = registry[name]
    installed.append({"name": name, "installed_at": entry.get("version", "unknown")})
    state["installed"] = installed
    _write_state(state)
    return {"ok": True, "package": entry}


@router.post("/remove")
async def remove_package(
    payload: dict[str, Any],
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name required")
    state = _load_state()
    state["installed"] = [pkg for pkg in state.get("installed", []) if pkg.get("name") != name]
    _write_state(state)
    return {"ok": True}


__all__ = ["router"]
