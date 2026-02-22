"""Decision insight routes."""

from typing import Any, Dict, List

from fastapi import APIRouter

from .. import context

router = APIRouter()


@router.get("/")
def list_decisions() -> List[Dict[str, Any]]:
    """Return the most recently dispatched actions."""
    return list(context.dispatch_log)


@router.post("/")
def propose_decision(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Request a new prescriptive decision using the provided context payload."""
    return context.proposed_actions(payload)
