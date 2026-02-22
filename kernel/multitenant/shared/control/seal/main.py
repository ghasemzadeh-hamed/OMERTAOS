import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from ..core.profiles import load_profile
from ..core.router import decide
from .orchestrator import get_status, run_job

load_dotenv()

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
PROFILE_NAME = os.getenv("PROFILE", "enterprise-vip")
BASE_DIR = Path(__file__).resolve().parents[3]
JOBS: Dict[str, Dict[str, Any]] = {}


def check_auth(header: Optional[str]) -> bool:
    if not ADMIN_TOKEN:
        return True
    if not header or not header.startswith("Bearer "):
        return False
    return header[7:] == ADMIN_TOKEN


class SealJob(BaseModel):
    model_id: str
    task_id: str
    objective: Dict[str, Any] = {"metric": "accuracy", "delta_min": 0.02}
    budget: Dict[str, Any] = {"gpus": 1, "max_steps": 200, "max_hours": 2}
    strategy: Dict[str, Any] = {"update": "lora", "adapter_rank": 8}


router = APIRouter()


@router.get("/healthz")
async def healthz():
    profile = load_profile(PROFILE_NAME, str(BASE_DIR))
    mode = profile.get("features", {}).get("router", {}).get("default_mode", "auto")
    return {"ok": True, "profile": profile.get("name", PROFILE_NAME), "router_mode": decide(mode, {"local_ok": True, "api_ok": True}), "jobs": len(JOBS)}


@router.post("/v1/seal/jobs")
async def create_job(req: SealJob, authorization: Optional[str] = Header(default=None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=403, detail="forbidden")
    job_id = os.urandom(8).hex()
    JOBS[job_id] = {"state": "queued", "events": [], "req": req.model_dump()}
    asyncio.create_task(run_job(job_id, JOBS))
    return {"job_id": job_id}


@router.get("/v1/seal/jobs/{job_id}/status")
async def status(job_id: str, authorization: Optional[str] = Header(default=None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=403, detail="forbidden")
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="not found")
    return JSONResponse(get_status(job_id, JOBS))


@router.get("/v1/seal/streams/{job_id}")
async def streams(job_id: str, authorization: Optional[str] = Header(default=None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=403, detail="forbidden")
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="not found")

    async def gen():
        for event in JOBS[job_id].get("events", []):
            yield f"data: {json.dumps(event)}\n\n"
        while JOBS[job_id]["state"] not in ("finished", "failed"):
            yield f"data: {json.dumps({'t': time.time(), 'msg': 'heartbeat'})}\n\n"
            await asyncio.sleep(1.0)
        yield f"data: {json.dumps({'state': JOBS[job_id]['state']})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.post("/v1/router/policy/reload")
async def policy_reload(authorization: Optional[str] = Header(default=None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=403, detail="forbidden")
    profile = load_profile(PROFILE_NAME, str(BASE_DIR))
    return {"ok": True, "profile": profile.get("name", PROFILE_NAME)}


app = FastAPI(title="SEAL Control", version="0.2.0")
app.include_router(router)
