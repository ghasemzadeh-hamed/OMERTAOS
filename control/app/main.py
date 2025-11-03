"""FastAPI application entrypoint for the control plane."""
from __future__ import annotations

import asyncio

from fastapi import FastAPI

try:  # pragma: no cover - compatibility with legacy package layout
    from app.routes import (
        admin_onboarding_router,
        ai_chat_router,
        agent_router,
        kernel_router,
        memory_router,
        models_router,
        rag_router,
    )
except Exception:  # pragma: no cover
    from routes import (  # type: ignore
        admin_onboarding_router,
        ai_chat_router,
        agent_router,
        kernel_router,
        memory_router,
        models_router,
        rag_router,
    )

from .api import (
    datasources_router,
    health_router,
    modules_router,
    providers_router,
    router_policy_router,
    webhook_router,
)
from .core.deps import get_state
from .core.tenancy import tenancy_middleware
from .core.workers import worker_loop

from aionos_control.routes import router as plugins_router

app = FastAPI(title="AION Control API")

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
app.include_router(webhook_router)
