from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from .decision import DecisionRouter, get_router
from .executors import execute_request, stream_request
from .schemas import ErrorResponse, InferenceRequest

logger = logging.getLogger("agentos.core")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.router = await get_router()
    logger.info("Decision router initialized")
    yield


app = FastAPI(title="AgentOS Control Plane", lifespan=lifespan)


@app.post("/dispatch")
async def dispatch(request: InferenceRequest) -> JSONResponse:
    router: DecisionRouter = app.state.router
    decision = await router.route(request)
    logger.info("request=%s route=%s reason=%s", request.request_id, decision.route, decision.reason)

    response = await execute_request(request, decision)
    return JSONResponse(response.dict())


@app.post("/stream")
async def stream(request: InferenceRequest) -> StreamingResponse:
    router: DecisionRouter = app.state.router
    decision = await router.route(request)
    logger.info("stream request=%s route=%s", request.request_id, decision.route)

    async def event_generator() -> AsyncIterator[bytes]:
        try:
            async for chunk in stream_request(request, decision):
                yield (chunk.json() + "\n").encode("utf-8")
        except HTTPException as exc:  # pragma: no cover - surfaced via gateway
            error = ErrorResponse(error="execution_failed", message=str(exc.detail))
            yield (error.json() + "\n").encode("utf-8")

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    await asyncio.sleep(0)
    return {"status": "ok"}
