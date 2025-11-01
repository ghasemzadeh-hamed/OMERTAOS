"""Provider management endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..core.deps import get_state
from ..core.state import ControlState, Provider
from ..schemas.provider import ProviderCreate, ProviderOut

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.post("", response_model=ProviderOut, status_code=201)
async def add_provider(
    payload: ProviderCreate,
    state: ControlState = Depends(get_state),
) -> ProviderOut:
    provider = Provider(
        name=payload.name,
        kind=payload.kind,
        base_url=str(payload.base_url),
        models=payload.models,
        api_key=payload.api_key,
    )
    await state.add_provider(provider)
    return ProviderOut(**payload.dict(), enabled=provider.enabled)


@router.post("/{name}/enable", response_model=ProviderOut)
async def enable_provider(
    name: str,
    state: ControlState = Depends(get_state),
) -> ProviderOut:
    if name not in state.providers:
        raise HTTPException(status_code=404, detail="provider not found")
    await state.enable_provider(name, True)
    provider = state.providers[name]
    return ProviderOut(**provider.__dict__)


@router.get("", response_model=List[ProviderOut])
async def list_providers(state: ControlState = Depends(get_state)) -> List[ProviderOut]:
    return [ProviderOut(**provider.__dict__) for provider in state.providers.values()]


@router.get("/{name}/health")
async def provider_health(name: str, state: ControlState = Depends(get_state)) -> dict:
    provider = state.providers.get(name)
    if provider is None:
        raise HTTPException(status_code=404, detail="provider not found")
    return {"status": "ok" if provider.enabled else "disabled"}
