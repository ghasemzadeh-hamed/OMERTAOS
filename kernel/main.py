"""FastAPI entrypoint for the AION-OS kernel service."""

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.kernel.dev_qwen_coder_kernel import dev_kernel_handle

app = FastAPI(title="AION-OS Kernel", version="0.1.0")


class KernelRequest(BaseModel):
    message: str = Field(..., description="User message or intent to process")
    metadata: Dict[str, Any] | None = Field(default=None, description="Optional contextual metadata")


class KernelResponse(BaseModel):
    type: str
    content: Any


def _handle_request_default(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "text", "content": "Default kernel handler is not configured."}


def _select_handler() -> Any:
    profile = os.getenv("AION_KERNEL_PROFILE", "default")
    if profile == "dev-qwen-coder":
        return dev_kernel_handle
    return _handle_request_default


@app.post("/kernel", response_model=KernelResponse)
async def invoke_kernel(request: KernelRequest) -> Dict[str, Any]:
    handler = _select_handler()
    result = handler({"message": request.message, "metadata": request.metadata or {}})
    if not isinstance(result, dict) or "type" not in result or "content" not in result:
        raise HTTPException(status_code=500, detail="Kernel handler returned invalid response.")
    return result


@app.get("/healthz")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "profile": os.getenv("AION_KERNEL_PROFILE", "default")}


__all__ = ["app"]
