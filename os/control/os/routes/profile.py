"""Profile selection endpoints."""
from __future__ import annotations

import os
from fastapi import APIRouter, Header, HTTPException, status

from os.control.aionos_profiles import read_profile_state, set_profile_state

router = APIRouter(prefix="/v1/config", tags=["config-profile"])

_ADMIN_TOKEN = (
    os.getenv("AION_ADMIN_TOKEN")
    or os.getenv("AUTH_TOKEN")
    or os.getenv("ADMIN_TOKEN")
    or ""
)


def _is_authorized(auth_header: str | None) -> bool:
    if not _ADMIN_TOKEN:
        return True
    if not auth_header:
        return False
    if not auth_header.lower().startswith("bearer "):
        return False
    return auth_header[7:] == _ADMIN_TOKEN


@router.get("/profile")
async def get_profile() -> dict[str, object]:
    profile, setup_done = read_profile_state()
    return {"profile": profile, "setupDone": setup_done}


@router.post("/profile")
async def set_profile(
    payload: dict[str, object],
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    if not _is_authorized(authorization):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    profile = str(payload.get("profile", "")).strip().lower()
    if profile not in ("user", "professional", "enterprise-vip"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid profile")
    setup_done = bool(payload.get("setupDone", True))
    set_profile_state(profile, setup_done=setup_done)
    return {"ok": True, "profile": profile, "setupDone": setup_done}
