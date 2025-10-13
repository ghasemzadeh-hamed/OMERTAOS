from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ExecutionRoute(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"
    HYBRID = "hybrid"


class InferenceRequest(BaseModel):
    request_id: str = Field(..., description="Unique identifier for tracing")
    prompt: str = Field(..., description="Textual prompt or instruction")
    task_type: str = Field("general", description="High level task intent")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RouterDecision(BaseModel):
    route: ExecutionRoute
    reason: str
    model_hint: Optional[str] = None


class InferenceResponse(BaseModel):
    request_id: str
    route: ExecutionRoute
    output: str
    latency_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    request_id: str
    route: ExecutionRoute
    sequence: int
    chunk: str
    is_final: bool = False


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
