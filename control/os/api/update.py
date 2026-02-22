"""Update center endpoints."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from .security import admin_required, admin_or_devops_required


router = APIRouter(prefix="/api/update", tags=["update"])


def _current_version() -> str:
    version_file = Path("VERSION")
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    try:
        return subprocess.check_output(["git", "describe", "--tags"], text=True).strip()
    except Exception:
        return "unknown"


@router.get("/status")
async def get_status(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    return {"current": _current_version()}


@router.post("/check")
async def check_updates(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    feed_url = os.getenv("AION_UPDATE_FEED_URL")
    if not feed_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="feed url not configured")
    async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
        response = await client.get(feed_url)
    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="update check failed")
    data = response.json()
    return {"current": _current_version(), "latest": data.get("latest"), "notes": data.get("notes")}


@router.post("/apply")
async def apply_update(principal=Depends(admin_required())) -> dict[str, Any]:
    script = Path(os.getenv("AION_UPDATE_SCRIPT", "scripts/update.sh"))
    if not script.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="update script missing")
    result = subprocess.run(["/bin/bash", str(script)], capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=result.stderr or "update failed")
    return {"ok": True, "output": result.stdout}


__all__ = ["router"]
