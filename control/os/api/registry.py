"""API endpoints for the consolidated AI registry catalog."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from os.control.os.registry import RegistryAggregator

from .security import admin_or_devops_required

router = APIRouter(prefix="/api/registry", tags=["registry"])


@router.get("")
async def get_registry(principal=Depends(admin_or_devops_required())) -> dict:
    """Return the combined registry catalog for all providers and templates."""
    aggregator = RegistryAggregator()
    return await aggregator.build()


__all__ = ["router"]
