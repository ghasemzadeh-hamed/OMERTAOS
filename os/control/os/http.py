"""FastAPI application entrypoint for the control plane."""
from __future__ import annotations

import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

import asyncio
import os

try:  # pragma: no cover - compatibility with legacy package layout
    from os.control.os.routes import (
        admin_onboarding_router,
        ai_chat_router,
        agent_router,
        config_router,
        profile_router,
        kernel_router,
        memory_router,
        models_router,
        rag_router,
        seal_router,
    )
except Exception:  # pragma: no cover
    from routes import (  # type: ignore
        admin_onboarding_router,
        ai_chat_router,
        agent_router,
        config_router,
        profile_router,
        kernel_router,
        memory_router,
        models_router,
        rag_router,
        seal_router,
    )

from os.control.os.api import (
    datasources_router,
    health_router,
    modules_router,
    providers_router,
    router_policy_router,
    webhook_router,
)
from os.control.os.api.files import router as files_router, data_router
from os.control.os.api.config import router as config_center_router, network_router
from os.control.os.api.metrics import router as metrics_router
from os.control.os.api.services import router as services_router
from os.control.os.api.logs import router as logs_router
from os.control.os.api.auth_admin import router as auth_router
from os.control.os.api.models import router as models_admin_router
from os.control.os.api.datasets import router as datasets_router
from os.control.os.api.packages import router as packages_router
from os.control.os.api.backup import router as backup_router
from os.control.os.api.update import router as update_router
from os.control.aionos_profiles import get_profile
from os.control.os.core.deps import get_state
from os.control.os.core.tenancy import tenancy_middleware
from os.control.os.core.workers import worker_loop

try:  # pragma: no cover - optional plugin bundle
    from aionos_control.routes import router as plugins_router
except ImportError:  # pragma: no cover
    from fastapi import APIRouter

    plugins_router = APIRouter()

app = FastAPI(title="AION Control API")


def _seal_enabled() -> bool:
    profile_name, _ = get_profile()
    return os.getenv("FEATURE_SEAL") == "1" or profile_name == "enterprise-vip"

app.middleware("http")(tenancy_middleware())


@app.on_event("startup")
async def start_workers() -> None:
    state = get_state()
    app.state.worker_shutdown = asyncio.Event()
    app.state.worker_task = asyncio.create_task(worker_loop(state, app.state.worker_shutdown))


@app.on_event("shutdown")
async def stop_workers() -> None:
    shutdown_event = getattr(app.state, "worker_shutdown", None)
    task = getattr(app.state, "worker_task", None)
    if shutdown_event is not None:
        shutdown_event.set()
    if task is not None:
        await task


async def _health_response() -> dict[str, str]:
    return {"status": "ok", "service": "control"}


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return await _health_response()


@app.get("/health")
async def health() -> dict[str, str]:
    return await _health_response()


try:  # pragma: no cover - optional dependency
    from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
except Exception:  # pragma: no cover
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    CollectorRegistry = None  # type: ignore
    generate_latest = None  # type: ignore


@app.get("/metrics")
async def metrics_endpoint() -> PlainTextResponse:
    if os.getenv("AION_METRICS_ENABLED", "1") not in {"1", "true", "TRUE"}:
        raise HTTPException(status_code=404, detail="metrics disabled")
    if generate_latest is None:
        raise HTTPException(status_code=503, detail="prometheus client not installed")
    registry = CollectorRegistry() if CollectorRegistry else None
    payload = generate_latest(registry) if registry else generate_latest()  # type: ignore[arg-type]
    return PlainTextResponse(payload, media_type=CONTENT_TYPE_LATEST)


app.include_router(admin_onboarding_router)
app.include_router(ai_chat_router)
app.include_router(agent_router)
app.include_router(config_router)
app.include_router(profile_router)
app.include_router(kernel_router)
app.include_router(memory_router)
app.include_router(models_router)
app.include_router(rag_router)

app.include_router(providers_router)
app.include_router(router_policy_router)
app.include_router(datasources_router)
app.include_router(modules_router)
app.include_router(health_router)
app.include_router(plugins_router)
if _seal_enabled():
    app.include_router(seal_router)
app.include_router(webhook_router)
app.include_router(files_router)
app.include_router(data_router)
app.include_router(config_center_router)
app.include_router(network_router)
app.include_router(metrics_router)
app.include_router(services_router)
app.include_router(logs_router)
app.include_router(auth_router)
app.include_router(models_admin_router)
app.include_router(datasets_router)
app.include_router(packages_router)
app.include_router(backup_router)
app.include_router(update_router)
