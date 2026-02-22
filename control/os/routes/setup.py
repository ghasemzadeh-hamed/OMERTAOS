"""Bootstrap setup endpoints for first-run onboarding."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from os.control.aion_profiles import read_bootstrap_state, set_bootstrap_state, set_profile_state

router = APIRouter(prefix="/v1/setup", tags=["setup"])


@router.get("/bootstrap")
async def get_bootstrap() -> dict[str, object]:
    return read_bootstrap_state()


@router.post("/bootstrap")
async def save_bootstrap(payload: dict[str, object]) -> dict[str, object]:
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    profile = str(payload.get("profile", "user")).strip().lower()
    encrypt_data = bool(payload.get("encryptData", True))

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username and password required")
    if profile not in {"user", "professional", "enterprise-vip"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid profile")

    defaults = {
        "totpIssuer": str(payload.get("totpIssuer") or "OMERTAOS"),
        "webauthnRpId": str(payload.get("webauthnRpId") or "localhost"),
        "recoveryEmail": str(payload.get("recoveryEmail") or f"{username}@local"),
    }
    set_profile_state(profile, setup_done=True)
    state = set_bootstrap_state(
        {
            "username": username,
            "profile": profile,
            "encryptData": encrypt_data,
            "defaults": defaults,
        }
    )
    return {"ok": True, **state}
