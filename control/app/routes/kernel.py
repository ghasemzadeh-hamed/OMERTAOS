"""FastAPI routes for managing kernel proposals."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..config import get_settings
from kernel import KernelController, KernelProposalStatus


class ScopeModel(BaseModel):
    type: str
    keys: List[str]
    target: str


class ChangeModel(BaseModel):
    key: str
    from_value: Optional[str] = Field(None, alias="from")
    to_value: str = Field(alias="to")

    class Config:
        populate_by_name = True


class CanaryModel(BaseModel):
    percent: int
    granularity: str


class GuardModel(BaseModel):
    degrade_threshold_pct: float


class ProposalModel(BaseModel):
    proposal_id: Optional[str] = None
    source: str = "kbrain"
    scope: ScopeModel
    changes: List[ChangeModel]
    ttl_seconds: int
    canary: CanaryModel
    risk_score: float
    expected_impact: Dict[str, float] = {}
    kpi_guard: GuardModel
    audit: Dict[str, Optional[str]] | None = None
    status: Optional[KernelProposalStatus] = None


settings = get_settings()
controller = KernelController(Path(settings.kernel_policy_file))
router = APIRouter(prefix="/v1/kernel", tags=["kernel"])


@router.post("/proposals")
def create_proposal(payload: ProposalModel):
    proposal = controller.submit_external_proposal(payload.dict(by_alias=True))
    return controller.serialize_proposal(proposal)


@router.get("/proposals")
def list_proposals(status: Optional[str] = None):
    return [controller.serialize_proposal(proposal) for proposal in controller.list_proposals(status)]


@router.post("/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: str):
    proposal = controller.approve(proposal_id, approver="admin")
    return controller.serialize_proposal(proposal)


@router.post("/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: str):
    proposal = controller.reject(proposal_id, approver="admin")
    return controller.serialize_proposal(proposal)


@router.post("/proposals/{proposal_id}/apply-now")
def apply_now(proposal_id: str):
    try:
        proposal = controller.apply(proposal_id)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return controller.serialize_proposal(proposal)
