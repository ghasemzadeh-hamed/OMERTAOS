"""SEAL orchestration endpoints for Enterprise-VIP."""
from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status

from app.control.aionos_profiles import get_profile
from app.control.app.policy import policy_store

router = APIRouter(prefix="/v1/seal", tags=["seal"])

_JOBS: Dict[str, Dict[str, Any]] = {}
_REGISTRY_ROOT = Path(os.getenv("AION_REGISTRY_DIR", "ai_registry")) / "storage" / "experiments"
_SEAL_CONFIG_DIR = Path(os.getenv("SEAL_CONFIG_DIR", "configs"))
_LOCK = asyncio.Lock()


def _seal_enabled() -> bool:
    profile_name, _ = get_profile()
    return os.getenv("FEATURE_SEAL") == "1" or profile_name == "enterprise-vip"


def _require_admin(request: Request) -> None:
    expected = os.getenv("AION_ADMIN_TOKEN") or os.getenv("AUTH_TOKEN")
    if not expected:
        return
    header = request.headers.get("authorization", "")
    token = header.replace("Bearer", "").strip()
    if token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


def _persist_artifacts(job_id: str, payload: Dict[str, Any]) -> None:
    target_dir = _REGISTRY_ROOT / job_id
    target_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "job_id": job_id,
        "created_at": time.time(),
        "payload": payload,
        "configs": {
            "seal": (_SEAL_CONFIG_DIR / "seal-default.yaml").read_text()
            if (_SEAL_CONFIG_DIR / "seal-default.yaml").exists()
            else None,
            "rollout": (_SEAL_CONFIG_DIR / "rollout-policy.yaml").read_text()
            if (_SEAL_CONFIG_DIR / "rollout-policy.yaml").exists()
            else None,
        },
    }
    (target_dir / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True))
    adapter_path = target_dir / "adapter.safetensors"
    if not adapter_path.exists():
        adapter_path.write_bytes(b"")


async def _advance_job(job_id: str) -> None:
    async with _LOCK:
        job = _JOBS[job_id]
        phases = [
            "queued",
            "inner_loop",
            "evaluation",
            "safety",
            "canary",
            "complete",
        ]
        for phase in phases:
            job["status"] = phase
            job["history"].append({"ts": time.time(), "status": phase})
            if phase == "canary":
                policy_store.reload()
            await asyncio.sleep(0)


def _ensure_enabled() -> None:
    if not _seal_enabled():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="seal disabled")


@router.post("/jobs")
async def create_job(request: Request, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    _ensure_enabled()
    _require_admin(request)
    data = payload or {}
    job_id = uuid4().hex
    job_record = {
        "job_id": job_id,
        "status": "pending",
        "created_at": time.time(),
        "history": [{"ts": time.time(), "status": "pending"}],
        "input": data,
    }
    async with _LOCK:
        _JOBS[job_id] = job_record
    _persist_artifacts(job_id, data)
    asyncio.create_task(_advance_job(job_id))
    return {"job_id": job_id, "status": job_record["status"]}


@router.get("/jobs/{job_id}/status")
async def job_status(job_id: str) -> Dict[str, Any]:
    _ensure_enabled()
    async with _LOCK:
        job = _JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
        return job


@router.get("/streams/{job_id}")
async def job_stream(job_id: str) -> Dict[str, Any]:
    _ensure_enabled()
    async with _LOCK:
        job = _JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
        return {"job_id": job_id, "events": job["history"]}


@router.post("/router/policy/reload")
async def reload_router_policy(request: Request) -> Dict[str, Any]:
    _ensure_enabled()
    _require_admin(request)
    policy_store.reload()
    return {"ok": True, "reloaded": True}
