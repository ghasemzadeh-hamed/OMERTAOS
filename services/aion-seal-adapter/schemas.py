from __future__ import annotations

from pydantic import BaseModel, Field

SCHEMA_VERSION = "v1"


class SealRunResponse(BaseModel):
    schema_version: str = Field(default=SCHEMA_VERSION)
    status: str
    model_path: str | None = None
    score: float | None = None
    detail: str | None = None


class HealthResponse(BaseModel):
    schema_version: str = Field(default=SCHEMA_VERSION)
    status: str
    service: str
