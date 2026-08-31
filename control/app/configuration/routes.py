from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from sqlalchemy.orm import Session

from control.app.network.models import get_db, init_db
from control.app.service_auth import require_gateway_service_token

from .schemas import ConfigurationProposal
from .service import apply, propose, revert, status

router = APIRouter(prefix="/v1/config", tags=["configuration"])


def require_admin(request: Request) -> None:
    require_gateway_service_token(request)


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
