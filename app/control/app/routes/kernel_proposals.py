from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.kernel.runtime import get_runtime


class ProposalRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    proposal_id: str
    source: str
    scope: Dict[str, object]
    changes: List[Dict[str, object]]
    ttl_seconds: int = Field(ge=0)
    canary: Dict[str, object]
    risk_score: float = Field(ge=0)
    expected_impact: Dict[str, float] = Field(default_factory=dict)
    kpi_guard: Dict[str, float]
    audit: Dict[str, object]


class AdminActionRequest(BaseModel):
    actor: str = Field(..., description="Admin actor performing the action")
    reason: Optional[str] = Field(default=None, description="Optional reason for the action")


router = APIRouter(prefix="/kernel", tags=["kernel"])


@router.post("/proposals")
def submit_proposal(payload: ProposalRequest) -> Dict[str, object]:
    try:
        return get_runtime().proposals.submit(payload.model_dump(by_alias=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/proposals")
def list_proposals(status: Optional[str] = None) -> List[Dict[str, object]]:
    try:
        return list(get_runtime().proposals.list(status=status))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/proposals/{proposal_id}")
def get_proposal(proposal_id: str) -> Dict[str, object]:
    try:
        return get_runtime().proposals.get(proposal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc


@router.post("/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: str, payload: AdminActionRequest) -> Dict[str, object]:
    try:
        return get_runtime().proposals.approve(proposal_id, payload.actor)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: str, payload: AdminActionRequest) -> Dict[str, object]:
    if not payload.reason:
        raise HTTPException(status_code=400, detail="reason is required to reject a proposal")
    try:
        return get_runtime().proposals.reject(proposal_id, payload.actor, payload.reason)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/proposals/{proposal_id}/apply-now")
def apply_now(proposal_id: str, payload: AdminActionRequest) -> Dict[str, object]:
    try:
        return get_runtime().proposals.apply_now(proposal_id, payload.actor)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="proposal not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
