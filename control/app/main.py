from __future__ import annotations

from fastapi import FastAPI

from control.app.network.routes import router as network_proxy_router

app = FastAPI(title="OMERTAOS Control Plane", version="0.1.0")
app.include_router(network_proxy_router)


def health_payload() -> dict[str, str]:
    return {"status": "ok", "service": "control"}


@app.get("/health")
@app.get("/healthz")
@app.get("/v1/health")
@app.get("/v1/healthz")
async def health() -> dict[str, str]:
    return health_payload()


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
