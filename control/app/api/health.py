"""Health and diagnostics endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.deps import get_state
from ..core.state import ControlState

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health(state: ControlState = Depends(get_state)) -> dict:
    return state.get_health_summary()


@router.get("/api/jobs")
async def jobs(state: ControlState = Depends(get_state)) -> dict:
    return {
        "items": [
            {
                "event_id": job.event_id,
                "event_type": job.event_type,
                "status": job.status,
                "detail": job.detail,
                "timestamp": job.timestamp,
            }
            for job in state.jobs
        ]
    }
