from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, List
from uuid import uuid4

sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict

from .config import get_settings
from .models import Task
from .orchestrator import orchestrator
from .policy import policy_store
from .routes.kernel import router as kernel_router
from .routes.memory import router as memory_router
from .routes.models import router as models_router


class SubmitRequest(BaseModel):
    schema_version: str = "1.0"
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())
    schemaVersion: str | None = None
    intent: str
    params: Dict[str, object]
    preferred_engine: str = "auto"
    priority: str = "normal"
    sla: Dict[str, object] = {}
    metadata: Dict[str, object] = {}


app = FastAPI(title="aionOS Control", version="1.0.0")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kernel_router)
app.include_router(memory_router)
app.include_router(models_router)


@app.middleware("http")
async def trace_context(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-request-id"] = request.headers.get("x-request-id", "")
    return response


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


def serialize_task(task: Task) -> Dict[str, object]:
    return {
        "schema_version": task.schema_version,
        "task_id": task.task_id,
        "intent": task.intent,
        "params": task.params,
        "status": task.status.value,
        "engine": {
            "route": task.engine_route,
            "reason": task.engine_reason,
            "chosen_by": task.engine_chosen_by,
            "tier": task.engine_tier,
        },
        "result": task.result,
        "usage": task.usage,
        "error": task.error,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@app.post(f"{settings.api_prefix}/tasks")
async def submit_task(payload: SubmitRequest):
    task = orchestrator.create_task(
        {
            **payload.model_dump(by_alias=True),
            "schema_version": payload.schemaVersion or payload.schema_version,
            "task_id": f"task-{uuid4()}",
        }
    )
    await orchestrator.execute(task)
    return serialize_task(task)


@app.get(f"{settings.api_prefix}/tasks")
async def list_tasks() -> List[Dict[str, object]]:
    return [serialize_task(task) for task in orchestrator.list_tasks()]


@app.get(f"{settings.api_prefix}/tasks/{{task_id}}")
async def get_task(task_id: str):
    task = orchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return serialize_task(task)


async def stream_generator(task_id: str) -> AsyncGenerator[bytes, None]:
    for _ in range(5):
        task = orchestrator.get_task(task_id)
        if task:
            payload = JSONResponse(content={"status": task.status.value}).body.decode()
            yield f"data: {payload}\n\n".encode()
        await asyncio.sleep(1)
    yield "data: {\"event\": \"completed\"}\n\n".encode()


@app.get(f"{settings.api_prefix}/stream/{{task_id}}")
async def stream_task(task_id: str):
    headers = {"Content-Type": "text/event-stream"}
    return StreamingResponse(stream_generator(task_id), headers=headers)


@app.post(f"{settings.api_prefix}/router/policy/reload")
async def reload_policy():
    policy_store.reload()
    return {"status": "reloaded", "policies": list(policy_store.to_json().keys())}


@app.get(f"{settings.api_prefix}/policies")
async def read_policies():
    return policy_store.to_json()


@app.put(f"{settings.api_prefix}/policies")
async def update_policies(payload: Dict[str, object]):
    policy_store.update_policies(payload)  # updates in-memory cache
    return policy_store.to_json()
