from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import AsyncIterator

from fastapi import HTTPException

from .schemas import ExecutionRoute, InferenceRequest, InferenceResponse, RouterDecision, StreamChunk

RUST_PROJECT = Path(__file__).resolve().parents[2] / "rust_modules" / "processor"


async def execute_request(request: InferenceRequest, decision: RouterDecision) -> InferenceResponse:
    started = time.perf_counter()

    if decision.route == ExecutionRoute.LOCAL:
        output = await _run_local_module(request)
    elif decision.route == ExecutionRoute.REMOTE:
        output = await _call_remote_model(request, decision)
    else:
        output = await _run_hybrid_pipeline(request)

    latency_ms = (time.perf_counter() - started) * 1000
    return InferenceResponse(
        request_id=request.request_id,
        route=decision.route,
        output=output,
        latency_ms=latency_ms,
        metadata={"decision_reason": decision.reason, "model_hint": decision.model_hint},
    )


async def stream_request(request: InferenceRequest, decision: RouterDecision) -> AsyncIterator[StreamChunk]:
    if decision.route == ExecutionRoute.HYBRID:
        async for chunk in _stream_hybrid_pipeline(request):
            yield chunk
        return

    output = await execute_request(request, decision)
    yield StreamChunk(
        request_id=request.request_id,
        route=decision.route,
        sequence=0,
        chunk=output.output,
        is_final=True,
    )


async def _run_local_module(request: InferenceRequest) -> str:
    payload = {
        "operation": request.task_type,
        "text": request.prompt,
        "parameters": request.parameters,
    }

    manifest_path = RUST_PROJECT / "Cargo.toml"
    if not manifest_path.exists():
        raise HTTPException(status_code=500, detail="Local module not built")

    process = await asyncio.create_subprocess_exec(
        "cargo",
        "run",
        "--quiet",
        "--manifest-path",
        str(manifest_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate(json.dumps(payload).encode("utf-8"))
    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Local module error: {stderr.decode().strip()}")

    response = json.loads(stdout.decode("utf-8"))
    return response.get("result", "")


async def _call_remote_model(request: InferenceRequest, decision: RouterDecision) -> str:
    await asyncio.sleep(0.1)
    return f"[remote:{decision.model_hint}] {request.prompt[::-1]}"


async def _run_hybrid_pipeline(request: InferenceRequest) -> str:
    local_result = await _run_local_module(
        InferenceRequest(
            request_id=f"{request.request_id}-local",
            prompt=request.prompt[: len(request.prompt) // 2],
            task_type="preprocess",
            parameters=request.parameters,
            metadata=request.metadata,
        )
    )

    hybrid_prompt = f"{local_result}\n---\n{request.prompt}"
    return await _call_remote_model(
        InferenceRequest(
            request_id=request.request_id,
            prompt=hybrid_prompt,
            task_type=request.task_type,
            parameters=request.parameters,
            metadata=request.metadata,
        ),
        RouterDecision(route=ExecutionRoute.REMOTE, reason="Hybrid downstream", model_hint="hybrid-remote"),
    )


async def _stream_hybrid_pipeline(request: InferenceRequest) -> AsyncIterator[StreamChunk]:
    preamble = "Routing via hybrid pipeline\n"
    yield StreamChunk(request_id=request.request_id, route=ExecutionRoute.HYBRID, sequence=0, chunk=preamble)

    local_result = await _run_local_module(
        InferenceRequest(
            request_id=f"{request.request_id}-local",
            prompt=request.prompt,
            task_type="summarize",
            parameters=request.parameters,
            metadata=request.metadata,
        )
    )
    yield StreamChunk(request_id=request.request_id, route=ExecutionRoute.HYBRID, sequence=1, chunk=local_result)

    remote = await _call_remote_model(request, RouterDecision(route=ExecutionRoute.REMOTE, reason="Hybrid final", model_hint="hybrid-final"))
    yield StreamChunk(request_id=request.request_id, route=ExecutionRoute.HYBRID, sequence=2, chunk=remote, is_final=True)
