"""API endpoints for tool recommendations sourced from LatentBox."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from os.control.os.core.deps import get_state
from os.control.os.core.state import ControlState
from os.control.os.recommendations import FEATURE_LATENTBOX, sync_latentbox_catalog
from os.control.os.schemas.recommendations import (
    ToolRecommendationResponse,
    ToolResource,
    ToolSyncResponse,
)

from .security import admin_or_devops_required

recommendations_router = APIRouter(prefix="/api/v1/recommendations/tools", tags=["recommendations"])


def _require_feature() -> None:
    if not FEATURE_LATENTBOX:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="latentbox recommendations disabled"
        )


@recommendations_router.get("", response_model=ToolRecommendationResponse)
async def recommend_tools(
    scenario: Optional[str] = None,
    capabilities: Optional[List[str]] = Query(default=None),
    constraints: Optional[List[str]] = Query(default=None),
    source: Optional[str] = Query(default="latentbox"),
    principal=Depends(admin_or_devops_required()),
    state: ControlState = Depends(get_state),
) -> ToolRecommendationResponse:
    _require_feature()
    results = await state.tool_store.recommend(
        source=source,
        scenario=scenario,
        capabilities=capabilities,
        constraints=constraints,
    )
    tools = [ToolResource(**record.__dict__) for record in results]
    return ToolRecommendationResponse(tools=tools)


@recommendations_router.post("/sync", response_model=ToolSyncResponse)
async def sync_latentbox(
    principal=Depends(admin_or_devops_required()),
    state: ControlState = Depends(get_state),
) -> ToolSyncResponse:
    _require_feature()
    stored = await sync_latentbox_catalog(state.tool_store)
    return ToolSyncResponse(synced=len(stored), source="latentbox")


__all__ = ["recommendations_router"]
