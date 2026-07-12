from __future__ import annotations

from fastapi import FastAPI

from control.app.health import router as health_router
from control.app.network.routes import router as network_proxy_router
from control.models.registry import get_model_registry

app = FastAPI(title="OMERTAOS Control Plane", version="0.1.0")
app.include_router(health_router)
app.include_router(network_proxy_router)


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
