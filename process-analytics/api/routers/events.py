"""API routes for ingesting events."""

from typing import Dict

from fastapi import APIRouter, HTTPException

from .. import context

router = APIRouter()


@router.post("/")
def ingest_event(event: Dict[str, object]) -> Dict[str, object]:
    """Normalize and store an incoming event."""
    try:
        normalized = context.ingestor.ingest(event)
    except ValueError as exc:  # validation errors
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    context.register_event(normalized)
    context.rebuild_discovery_model()
    return {"status": "accepted", "event": normalized}
