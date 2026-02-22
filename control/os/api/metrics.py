"""System metrics endpoints."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

import psutil
import httpx
from fastapi import APIRouter, Depends

from os.control.os.core.deps import get_state
from os.control.os.core.state import ControlState

from .security import admin_or_devops_required


router = APIRouter(prefix="/api/metrics", tags=["metrics"])


def _format_size(value: float) -> dict[str, float]:
    return {
        "bytes": value,
        "mb": round(value / (1024 * 1024), 2),
        "gb": round(value / (1024 * 1024 * 1024), 2),
    }


def _gpu_summary() -> list[dict[str, Any]]:
    try:
        import GPUtil  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        return []
    gpus = []
    for gpu in GPUtil.getGPUs():  # pragma: no cover - hardware specific
        gpus.append(
            {
                "id": gpu.id,
                "name": gpu.name,
                "memory_total_mb": gpu.memoryTotal,
                "memory_used_mb": gpu.memoryUsed,
                "utilization": gpu.load * 100,
                "temperature": gpu.temperature,
            }
        )
    return gpus


@router.get("/system")
async def system_metrics(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk_root = Path(os.getenv("AION_DISK_PATH", "/"))
    disk = psutil.disk_usage(str(disk_root))
    return {
        "cpu": {"percent": cpu_percent, "cores": psutil.cpu_count()},
        "memory": {
            "total": _format_size(memory.total),
            "used": _format_size(memory.used),
            "percent": memory.percent,
        },
        "disk": {
            "path": str(disk_root),
            "total": _format_size(disk.total),
            "used": _format_size(disk.used),
            "percent": disk.percent,
        },
        "gpu": _gpu_summary(),
    }


async def _check_health(url: str) -> str:
    timeout = httpx.Timeout(2.0, connect=1.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url)
            if response.status_code < 400:
                return "UP"
        except Exception:
            return "DOWN"
    return "DOWN"


SERVICES = {
    "gateway": os.getenv("AION_GATEWAY_HEALTH_URL", "http://gateway:8080/healthz"),
    "control": os.getenv("AION_CONTROL_HEALTH_URL", "http://localhost:8000/healthz"),
    "console": os.getenv("AION_CONSOLE_HEALTH_URL", "http://console:3000/api/healthz"),
    "kernel": os.getenv("AION_KERNEL_HEALTH_URL", "http://kernel:7000/healthz"),
}


@router.get("/services")
async def services_metrics(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    tasks = [asyncio.create_task(_check_health(url)) for url in SERVICES.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    payload = []
    for (name, url), status_value in zip(SERVICES.items(), results):
        status_str = "DOWN"
        if isinstance(status_value, str):
            status_str = status_value
        payload.append({"name": name, "url": url, "status": status_str})
    return {"services": payload}


@router.get("/agents")
async def agent_metrics(
    state: ControlState = Depends(get_state),
    principal=Depends(admin_or_devops_required()),
) -> dict[str, Any]:
    queue_depth = state.event_queue.qsize()
    jobs = list(state.jobs)
    running = len([job for job in jobs if job.status == "running"])
    return {
        "running_agents": running,
        "queued_tasks": queue_depth,
        "recent_jobs": [
            {
                "event_id": job.event_id,
                "status": job.status,
                "detail": job.detail,
                "timestamp": job.timestamp,
            }
            for job in jobs[-20:]
        ],
    }


__all__ = ["router"]
