from __future__ import annotations

import os
import secrets

from fastapi import HTTPException, Request, status


def gateway_service_token_matches(request: Request) -> bool:
    authorization = request.headers.get("authorization") or ""
    if not authorization.startswith("Bearer "):
        return False
    token = authorization.removeprefix("Bearer ")
    configured = (
        os.getenv("AION_GATEWAY_ADMIN_TOKEN") or os.getenv("AION_ADMIN_TOKEN") or ""
    )
    return bool(configured and secrets.compare_digest(token, configured))


def require_gateway_service_token(request: Request) -> None:
    if not gateway_service_token_matches(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trusted Gateway authentication required",
        )
