from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextlib import suppress

from control.app.setup.routes import router as setup_router

from fastapi import FastAPI

from control.app.configuration.routes import router as configuration_router
from control.app.health import router as health_router
from control.app.network.models import init_db
from control.app.network.routes import router as network_proxy_router
from control.app.runtime_nodes.lifecycle import (
    RuntimeLifecycleConfig,
    RuntimeLifecycleManager,
)
from control.app.runtime_nodes.routes import router as runtime_nodes_router
from control.models.registry import get_model_registry


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    init_db()
    configs = RuntimeLifecycleConfig.all_from_env()
    task: asyncio.Task[None] | None = None
    if configs:
        lifecycle = RuntimeLifecycleManager(configs)
        task = asyncio.create_task(lifecycle.run(), name="runtime-node-lifecycle")
        application.state.runtime_lifecycle_task = task
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            del application.state.runtime_lifecycle_task


app = FastAPI(title="OMERTAOS Control Plane", version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(configuration_router)
app.include_router(network_proxy_router)
app.include_router(runtime_nodes_router)
app.include_router(setup_router)


@app.get("/v1/tasks/{task_id}")
async def task_status(task_id: str) -> dict[str, object]:
    return {
        "schemaVersion": "1.0",
        "taskId": task_id,
        "intent": "status",
        "status": "PENDING",
        "engine": {
            "route": "control",
            "chosen_by": "control",
            "reason": "gRPC task API placeholder",
        },
        "result": {},
        "error": None,
    }


@app.get("/models")
@app.get("/v1/models")
async def list_models() -> list[dict[str, object]]:
    """Return normalized metadata from the canonical model-profile directory."""

    return get_model_registry().list_models()
