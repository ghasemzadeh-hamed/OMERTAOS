"""Router policy endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..core.deps import get_state
from ..core.state import ControlState, RouterPolicy, RouterPolicySnapshot
from ..schemas.router_policy import (
    RouterPolicyDocument,
    RouterPolicyHistory,
    RouterPolicyResponse,
)

router = APIRouter(prefix="/api/router", tags=["router"])


def _map_history(entries: list[RouterPolicySnapshot]) -> list[RouterPolicyHistory]:
    return [
        RouterPolicyHistory(
            revision=entry.revision,
            checksum=entry.checksum,
            version=entry.version,
            applied_at=entry.applied_at,
        )
        for entry in entries
    ]


def _build_document(policy: RouterPolicy) -> RouterPolicyDocument:
    payload = policy.document or {}
    return RouterPolicyDocument(
        version=str(payload.get("version", policy.version)),
        default=payload.get("default", "local"),
        rules=payload.get("rules", []),
        budgets=payload.get("budgets"),
    )


@router.get("/policy", response_model=RouterPolicyResponse)
async def get_policy(state: ControlState = Depends(get_state)) -> RouterPolicyResponse:
    policy = state.router_policy
    return RouterPolicyResponse(
        revision=policy.revision,
        checksum=policy.checksum,
        document=_build_document(policy),
        history=_map_history(state.get_router_policy_history()),
    )


@router.post("/policy", response_model=RouterPolicyResponse)
async def set_policy(
    document: RouterPolicyDocument,
    state: ControlState = Depends(get_state),
) -> RouterPolicyResponse:
    policy = await state.set_router_policy(document.dict())
    return RouterPolicyResponse(
        revision=policy.revision,
        checksum=policy.checksum,
        document=_build_document(policy),
        history=_map_history(state.get_router_policy_history()),
    )


@router.post("/policy/reload")
async def reload_policy(state: ControlState = Depends(get_state)) -> dict:
    return {"status": "ok", "revision": state.router_policy.revision}


@router.post("/policy/rollback", response_model=RouterPolicyResponse)
async def rollback_policy(
    state: ControlState = Depends(get_state),
    revision: int | None = None,
) -> RouterPolicyResponse:
    try:
        policy = await state.rollback_router_policy(revision)
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RouterPolicyResponse(
        revision=policy.revision,
        checksum=policy.checksum,
        document=_build_document(policy),
        history=_map_history(state.get_router_policy_history()),
    )
