"""FastAPI application entrypoint for the control plane."""
from __future__ import annotations

import asyncio

from fastapi import FastAPI

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
