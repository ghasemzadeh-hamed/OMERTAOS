"""Pydantic models for tool recommendations and latentbox resources."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


class ToolResource(BaseModel):
    id: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=1)
    category: constr(strip_whitespace=True, min_length=1)
    url: HttpUrl
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: constr(strip_whitespace=True, min_length=1) = "latentbox"
    scenarios: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    created_at: float
    updated_at: float

    class Config:
        orm_mode = True


class ToolRecommendationResponse(BaseModel):
    tools: List[ToolResource]


class ToolSyncResponse(BaseModel):
    synced: int
    source: str = "latentbox"
