"""Lightweight RBAC helpers for the control plane APIs."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable, Set

from fastapi import Depends, HTTPException, Request, status


_DEFAULT_ROLES = {
    role.strip().upper()
    for role in (os.getenv("AION_DEFAULT_ROLES") or "ROLE_USER").split(",")
    if role.strip()
}


@dataclass
class Principal:
    """Represents the authenticated caller.

    The control plane currently relies on upstream services (gateway or the
    console) to authenticate users.  They forward role information via HTTP
    headers which we normalize here so API handlers can enforce RBAC without
    knowing the concrete auth backend.
    """

    subject: str | None
    roles: Set[str]

    def has_any_role(self, required: Iterable[str]) -> bool:
        normalized = {role.upper() for role in required}
        return bool(self.roles.intersection(normalized))


def _extract_roles(request: Request) -> Set[str]:
    header_names = [
        "x-aion-roles",
        "x-omerta-roles",
        "x-user-roles",
        "x-user-role",
    ]
    roles: Set[str] = set()
    for header in header_names:
        raw = request.headers.get(header)
        if raw:
            parts = [part.strip().upper() for part in raw.split(",") if part.strip()]
            roles.update(parts)
    if not roles:
        roles.update(_DEFAULT_ROLES)
    return roles


def get_principal(request: Request) -> Principal:
    subject = request.headers.get("x-user-id") or request.headers.get("x-user-email")
    roles = _extract_roles(request)
    return Principal(subject=subject, roles=roles)


def require_roles(*required: str):
    """FastAPI dependency factory enforcing RBAC requirements."""

    async def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if not principal.has_any_role(required):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return principal

    return dependency


def admin_required() -> Depends:
    return require_roles("ROLE_ADMIN")


def admin_or_devops_required() -> Depends:
    return require_roles("ROLE_ADMIN", "ROLE_DEVOPS")


__all__ = [
    "Principal",
    "admin_required",
    "admin_or_devops_required",
    "get_principal",
    "require_roles",
]
