"""Router policy endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..core.deps import get_state
from ..core.state import ControlState
from ..schemas.router_policy import RouterPolicyDocument, RouterPolicyResponse

router = APIRouter(prefix="/api/router", tags=["router"])


@router.get("/policy", response_model=RouterPolicyResponse)
async def get_policy(state: ControlState = Depends(get_state)) -> RouterPolicyResponse:
    policy = state.router_policy
    return RouterPolicyResponse(revision=policy.revision, document=policy.document)


@router.post("/policy", response_model=RouterPolicyResponse)
async def set_policy(
    document: RouterPolicyDocument,
    state: ControlState = Depends(get_state),
) -> RouterPolicyResponse:
    policy = await state.set_router_policy(document.dict())
    return RouterPolicyResponse(revision=policy.revision, document=policy.document)


@router.post("/policy/reload")
async def reload_policy(state: ControlState = Depends(get_state)) -> dict:
    return {"status": "ok", "revision": state.router_policy.revision}


@router.post("/policy/rollback")
async def rollback_policy(state: ControlState = Depends(get_state)) -> dict:
    if state.router_policy.revision == 0:
        raise HTTPException(status_code=400, detail="no policy history available")
    # This stub simply reuses current policy without maintaining history.
    return {"status": "ok", "revision": state.router_policy.revision}
