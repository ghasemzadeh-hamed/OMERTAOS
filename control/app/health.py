from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


def health_payload() -> dict[str, str]:
    return {"status": "ok", "service": "control"}


@router.get("/health")
@router.get("/healthz")
@router.get("/v1/health")
@router.get("/v1/healthz")
async def health() -> dict[str, str]:
    return health_payload()
