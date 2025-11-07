"""ChatOps configuration proxy endpoints."""
from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status

from app.control.aionos_profiles import get_profile

router = APIRouter(prefix="/v1/config", tags=["config"])

_STATE: Dict[str, Any] = {"pending": None, "active": None, "history": []}
_CFG_DIR = Path(os.getenv("AION_CONFIG_DIR", "./configs"))
_LOCK = asyncio.Lock()


def _require_admin(request: Request) -> None:
    expected = os.getenv("AION_ADMIN_TOKEN") or os.getenv("AUTH_TOKEN")
    if not expected:
        return
    header = request.headers.get("authorization", "")
    token = header.replace("Bearer", "").strip()
    if token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


@router.post("/propose")
async def propose(patch: Dict[str, Any], request: Request) -> Dict[str, Any]:
    _require_admin(request)
    async with _LOCK:
        profile_name, profile_cfg = get_profile()
        now = time.time()
        item = {
            "ts": now,
            "patch": patch,
            "state": "proposed",
            "profile": profile_name,
            "router": profile_cfg.get("features", {}).get("router", {}),
        }
        _STATE["pending"] = item
        return {"ok": True, "pending": item}


@router.post("/apply")
async def apply(request: Request) -> Dict[str, Any]:
    _require_admin(request)
    async with _LOCK:
        if not _STATE["pending"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no pending proposal")
        item = dict(_STATE["pending"])
        item["state"] = "applied"
        _CFG_DIR.mkdir(parents=True, exist_ok=True)
        output_path = _CFG_DIR / "pending.json"
        output_path.write_text(json.dumps(item, indent=2, sort_keys=True))
        _STATE["active"] = item
        _STATE["history"].append(item)
        _STATE["pending"] = None
        return {"ok": True, "active": item}


@router.post("/revert")
async def revert(request: Request) -> Dict[str, Any]:
    _require_admin(request)
    async with _LOCK:
        _STATE["active"] = None
        pending_path = _CFG_DIR / "pending.json"
        if pending_path.exists():
            pending_path.unlink()
        return {"ok": True}


@router.get("/status")
async def status() -> Dict[str, Any]:
    async with _LOCK:
        return {
            "pending": _STATE["pending"],
            "active": _STATE["active"],
            "history_count": len(_STATE["history"]),
        }
