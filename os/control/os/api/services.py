"""Service orchestration endpoints."""
from __future__ import annotations

import asyncio
import os
import shlex
import subprocess
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from .security import admin_required, admin_or_devops_required


router = APIRouter(prefix="/api/services", tags=["services"])


DEFAULT_SERVICES = [
    {"name": "gateway", "display_name": "Gateway", "health_url": os.getenv("AION_GATEWAY_HEALTH_URL")},
    {"name": "control", "display_name": "Control", "health_url": os.getenv("AION_CONTROL_HEALTH_URL")},
    {"name": "console", "display_name": "Console", "health_url": os.getenv("AION_CONSOLE_HEALTH_URL")},
    {"name": "kernel", "display_name": "Kernel", "health_url": os.getenv("AION_KERNEL_HEALTH_URL")},
    {"name": "workers", "display_name": "Workers", "health_url": os.getenv("AION_WORKER_HEALTH_URL")},
]


async def _probe_service(service: dict[str, Any]) -> dict[str, Any]:
    status_value = "unknown"
    url = service.get("health_url")
    if url:
        from .metrics import _check_health  # local import to avoid cycle

        status_value = await _check_health(url)
    return {
        "name": service["name"],
        "display_name": service.get("display_name", service["name"].title()),
        "status": status_value,
    }


@router.get("")
async def list_services(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    configured = os.getenv("AION_SERVICES_CONFIG")
    services: list[dict[str, Any]] = []
    if configured:
        for chunk in configured.split(";"):
            if not chunk.strip():
                continue
            name, _, rest = chunk.partition(":")
            services.append({"name": name.strip(), "display_name": name.strip().title(), "health_url": rest.strip() or None})
    else:
        services = DEFAULT_SERVICES
    tasks = [asyncio.create_task(_probe_service(service)) for service in services]
    results = await asyncio.gather(*tasks)
    return {"services": results}


def _compose_command(name: str, action: str) -> list[str]:
    mode = (os.getenv("AION_SERVICE_CONTROL_MODE") or "disabled").lower()
    if mode == "docker":
        compose_file = os.getenv("AION_DOCKER_COMPOSE_FILE", "docker-compose.yml")
        return ["docker", "compose", "-f", compose_file, action, name]
    if mode == "systemd":
        unit_prefix = os.getenv("AION_SYSTEMD_PREFIX", "aion")
        return ["systemctl", action, f"{unit_prefix}-{name}.service"]
    if mode == "script":
        script = os.getenv("AION_SERVICE_CONTROL_SCRIPT")
        if not script:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="script not configured")
        return shlex.split(script) + [name, action]
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="service control disabled")


def _run_command(command: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(command, capture_output=True, check=False, text=True)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip()


@router.post("/{service_name}/action")
async def service_action(
    service_name: str = Path(..., alias="name"),
    payload: dict[str, str] | None = None,
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    action = (payload or {}).get("action")
    if action not in {"start", "stop", "restart"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid action")
    command = _compose_command(service_name, action)
    returncode, output = await asyncio.to_thread(_run_command, command)
    if returncode != 0:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=output or "command failed")
    return {"ok": True, "output": output}


__all__ = ["router"]
