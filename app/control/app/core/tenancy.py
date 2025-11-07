"""Helpers for propagating tenant context across the control plane."""
from __future__ import annotations

import os
from contextvars import ContextVar
from typing import Callable, Iterable, Optional

from fastapi import HTTPException, Request

TENANT_HEADER = "tenant-id"
LEGACY_TENANT_HEADERS: Iterable[str] = ("tenant-id", "x-tenant", "x-tenant-id")
TENANT_CONTEXT: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)


def _normalise(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def resolve_tenant_id(request: Request) -> Optional[str]:
    """Resolve the tenant identifier from HTTP headers."""

    for header_name in LEGACY_TENANT_HEADERS:
        value = request.headers.get(header_name)
        tenant = _normalise(value)
        if tenant:
            return tenant
    return None


def require_tenant_id() -> str:
    """Return the current tenant id or raise when tenancy is enforced."""

    tenant_id = TENANT_CONTEXT.get()
    mode = os.getenv("TENANCY_MODE", "single").lower()
    if mode == "multi" and not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant-ID header required")
    return tenant_id or "default"


def tenancy_middleware() -> Callable:
    """Create middleware that propagates the tenant context via contextvars."""

    mode = os.getenv("TENANCY_MODE", "single").lower()

    async def _middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        tenant_id = resolve_tenant_id(request)
        if mode == "multi" and tenant_id is None:
            raise HTTPException(status_code=400, detail="Tenant-ID header required")
        token = TENANT_CONTEXT.set(tenant_id)
        try:
            response = await call_next(request)
        finally:
            TENANT_CONTEXT.reset(token)
        if tenant_id:
            response.headers["Tenant-ID"] = tenant_id
        return response

    return _middleware


__all__ = [
    "LEGACY_TENANT_HEADERS",
    "TENANT_CONTEXT",
    "TENANT_HEADER",
    "resolve_tenant_id",
    "require_tenant_id",
    "tenancy_middleware",
]
