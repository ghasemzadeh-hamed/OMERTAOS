"""Pydantic models for agent catalog and lifecycle endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, constr


class AgentTemplate(BaseModel):
    id: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=1)
    category: constr(strip_whitespace=True, min_length=1)
    framework: constr(strip_whitespace=True, min_length=1)
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    icon: Optional[str] = None
    recipe: constr(strip_whitespace=True, min_length=1)
    config_schema: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        validate_assignment = True


class AgentCatalogResponse(BaseModel):
    agents: List[AgentTemplate]


class AgentTemplateResponse(BaseModel):
    template: AgentTemplate
    recipe: Dict[str, Any] = Field(default_factory=dict)


class AgentInstanceCreate(BaseModel):
    template_id: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=1)
    config: Dict[str, Any] = Field(default_factory=dict)
    scope: constr(strip_whitespace=True, min_length=1) = "tenant"
    enabled: bool = True


class AgentInstanceUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class AgentInstanceOut(BaseModel):
    id: str
    template_id: str
    tenant_id: str
    name: str
    config: Dict[str, Any]
    scope: str
    status: str
    enabled: bool
    created_at: float
    updated_at: float

    class Config:
        orm_mode = True
