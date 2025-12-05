"""Profile selection endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from os.control.aionos_profiles import read_profile_state, set_profile_state

router = APIRouter(prefix="/v1/config", tags=["config-profile"])


@router.get("/profile")
async def get_profile() -> dict[str, object]:
    """Return the canonical profile/setup state stored on disk.

    Authentication is enforced by the gateway; this handler only exposes the
    state persisted in `.aionos/profile.json` so all callers see a single
    source of truth for setup and profile selection.
    """

    profile, setup_done = read_profile_state()
    return {"profile": profile, "setupDone": setup_done}


@router.post("/profile")
async def set_profile(payload: dict[str, object]) -> dict[str, object]:
    """Persist the chosen profile/setup state.

    Auth decisions are made upstream (gateway middleware). This handler simply
    normalises and stores the provided profile flag so the console and gateway
    observe the same state.
    """

    profile = str(payload.get("profile", "")).strip().lower()
    if profile not in ("user", "professional", "enterprise-vip"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid profile")
    setup_done = bool(payload.get("setupDone", True))
    set_profile_state(profile, setup_done=setup_done)
    return {"ok": True, "profile": profile, "setupDone": setup_done}
