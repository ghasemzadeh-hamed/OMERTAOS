from __future__ import annotations

import os
import secrets

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    status as http_status,
)
from sqlalchemy.orm import Session

from control.app.network.models import get_db, init_db

from .schemas import ConfigurationProposal
from .service import apply, propose, revert, status

router = APIRouter(prefix="/v1/config", tags=["configuration"])


def _roles(x_aion_roles: str | None = Header(default=None)) -> set[str]:
    return {
        role.strip().lower() for role in (x_aion_roles or "").split(",") if role.strip()
    }


def _is_admin(request: Request, roles: set[str]) -> bool:
    token = (request.headers.get("authorization") or "").removeprefix("Bearer ")
    configured = (
        os.getenv("AION_GATEWAY_ADMIN_TOKEN") or os.getenv("AION_ADMIN_TOKEN") or ""
    )
    token_matches = bool(configured and secrets.compare_digest(token, configured))
    return "admin" in roles or token_matches


def require_admin(request: Request, roles: set[str] = Depends(_roles)) -> None:
    if not _is_admin(request, roles):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )


def _actor(request: Request) -> str:
    return (
        request.headers.get("x-aion-user-id")
        or request.headers.get("x-request-id")
        or "system"
    )


def _tenant(request: Request) -> str:
    return (
        request.headers.get("tenant-id")
        or request.headers.get("x-tenant-id")
        or "default"
    )


@router.on_event("startup")
def startup() -> None:
    init_db()


@router.get("/status")
def configuration_status(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
) -> dict[str, object]:
    return status(db)


@router.post("/propose")
def propose_configuration(
    payload: ConfigurationProposal,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
) -> dict[str, object]:
    return propose(db, payload, _actor(request), _tenant(request))


@router.post("/apply")
def apply_configuration(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
) -> dict[str, object]:
    return apply(db, _actor(request), _tenant(request))


@router.post("/revert")
def revert_configuration(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
) -> dict[str, object]:
    return revert(db, _actor(request), _tenant(request))
