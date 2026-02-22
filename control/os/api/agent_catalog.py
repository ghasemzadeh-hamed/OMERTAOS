"""Agent catalog and deployment endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from jsonschema import Draft7Validator, ValidationError

from os.control.os.agent_catalog import AgentCatalog
from os.control.os.core.deps import get_state
from os.control.os.core.state import ControlState
from os.control.os.core.tenancy import require_tenant_id
from os.control.os.schemas.agent import (
    AgentCatalogResponse,
    AgentInstanceCreate,
    AgentInstanceOut,
    AgentInstanceUpdate,
    AgentTemplateResponse,
)

from .security import admin_or_devops_required

catalog_router = APIRouter(prefix="/api/agent-catalog", tags=["agents"])
agents_router = APIRouter(prefix="/api/agents", tags=["agents"])
_catalog = AgentCatalog()


def _validate_config(template_schema: dict, payload: dict) -> None:
    if not template_schema:
        return
    try:
        validator = Draft7Validator(template_schema)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    try:
        validator.validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc


@catalog_router.get("", response_model=AgentCatalogResponse)
async def list_agent_templates(principal=Depends(admin_or_devops_required())) -> AgentCatalogResponse:
    templates = _catalog.list_templates()
    return AgentCatalogResponse(agents=templates)


@catalog_router.get("/{template_id}", response_model=AgentTemplateResponse)
async def get_agent_template(
    template_id: str, principal=Depends(admin_or_devops_required())
) -> AgentTemplateResponse:
    template = _catalog.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="template not found")
    recipe = _catalog.load_recipe(template.recipe)
    return AgentTemplateResponse(template=template, recipe=recipe)


@agents_router.get("", response_model=List[AgentInstanceOut])
async def list_agents(
    principal=Depends(admin_or_devops_required()),
    tenant_id: str = Depends(require_tenant_id),
    state: ControlState = Depends(get_state),
) -> List[AgentInstanceOut]:
    instances = await state.agent_registry.list(tenant_id)
    return [AgentInstanceOut(**instance.__dict__) for instance in instances]


@agents_router.post("", response_model=AgentInstanceOut, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: AgentInstanceCreate,
    principal=Depends(admin_or_devops_required()),
    tenant_id: str = Depends(require_tenant_id),
    state: ControlState = Depends(get_state),
) -> AgentInstanceOut:
    template = _catalog.get_template(payload.template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="template not found")
    _validate_config(template.config_schema, payload.config)
    instance = await state.agent_registry.create(
        tenant_id=tenant_id,
        template_id=payload.template_id,
        name=payload.name,
        config=payload.config,
        scope=payload.scope,
        enabled=payload.enabled,
    )
    return AgentInstanceOut(**instance.__dict__)


@agents_router.patch("/{agent_id}", response_model=AgentInstanceOut)
async def update_agent(
    agent_id: str,
    payload: AgentInstanceUpdate,
    principal=Depends(admin_or_devops_required()),
    tenant_id: str = Depends(require_tenant_id),
    state: ControlState = Depends(get_state),
) -> AgentInstanceOut:
    instance = await state.agent_registry.get(tenant_id, agent_id)
    if instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent not found")
    template = _catalog.get_template(instance.template_id)
    if template is not None and payload.config is not None:
        _validate_config(template.config_schema, payload.config)
    updated = await state.agent_registry.update(
        tenant_id,
        agent_id,
        name=payload.name if payload.name is not None else instance.name,
        config=payload.config if payload.config is not None else instance.config,
        enabled=payload.enabled if payload.enabled is not None else instance.enabled,
    )
    if updated is None:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent not found")
    return AgentInstanceOut(**updated.__dict__)


@agents_router.post("/{agent_id}/deploy", response_model=AgentInstanceOut)
async def deploy_agent(
    agent_id: str,
    principal=Depends(admin_or_devops_required()),
    tenant_id: str = Depends(require_tenant_id),
    state: ControlState = Depends(get_state),
) -> AgentInstanceOut:
    updated = await state.agent_registry.update(tenant_id, agent_id, status="active", enabled=True)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent not found")
    return AgentInstanceOut(**updated.__dict__)


@agents_router.post("/{agent_id}/disable", response_model=AgentInstanceOut)
async def disable_agent(
    agent_id: str,
    principal=Depends(admin_or_devops_required()),
    tenant_id: str = Depends(require_tenant_id),
    state: ControlState = Depends(get_state),
) -> AgentInstanceOut:
    updated = await state.agent_registry.update(tenant_id, agent_id, status="disabled", enabled=False)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent not found")
    return AgentInstanceOut(**updated.__dict__)


__all__ = ["catalog_router", "agents_router"]
