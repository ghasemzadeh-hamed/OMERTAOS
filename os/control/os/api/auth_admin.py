"""Administrative RBAC endpoints."""
from __future__ import annotations

import os
import secrets
from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Path, status

from .security import admin_required


router = APIRouter(prefix="/api/auth", tags=["auth"])

_POOL: asyncpg.Pool | None = None


async def _get_pool() -> asyncpg.Pool:
    global _POOL
    if _POOL is None:
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database not configured")
        _POOL = await asyncpg.create_pool(dsn)
        async with _POOL.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_tokens (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    scopes TEXT[] DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
    return _POOL


async def _fetch(conn: asyncpg.Connection, query: str, *args: Any) -> list[asyncpg.Record]:
    rows = await conn.fetch(query, *args)
    return list(rows)


@router.get("/roles")
async def list_roles(principal=Depends(admin_required())) -> dict[str, Any]:
    return {"roles": ["ROLE_ADMIN", "ROLE_MANAGER", "ROLE_DEVOPS", "ROLE_USER"]}


@router.get("/users")
async def list_users(principal=Depends(admin_required())) -> dict[str, Any]:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await _fetch(
            conn,
            'SELECT id, email, name, role, "createdAt" FROM "User" ORDER BY "createdAt" DESC',
        )
    return {
        "users": [
            {
                "id": row["id"],
                "email": row["email"],
                "name": row["name"],
                "role": row["role"],
                "created_at": row["createdAt"].isoformat() if row["createdAt"] else None,
            }
            for row in rows
        ]
    }


@router.post("/users/{user_id}/roles")
async def assign_role(
    user_id: str,
    payload: dict[str, str],
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    new_role = payload.get("role")
    if not new_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role required")
    pool = await _get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute('UPDATE "User" SET role=$1 WHERE id=$2', new_role, user_id)
    if result.endswith("UPDATE 0"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return {"ok": True, "role": new_role}


@router.get("/tokens")
async def list_tokens(principal=Depends(admin_required())) -> dict[str, Any]:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await _fetch(conn, "SELECT id, name, token, scopes, created_at FROM auth_tokens ORDER BY created_at DESC")
    return {
        "tokens": [
            {
                "id": row["id"],
                "name": row["name"],
                "token": row["token"],
                "scopes": row["scopes"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    }


@router.post("/tokens")
async def create_token(payload: dict[str, Any], principal=Depends(admin_required())) -> dict[str, Any]:
    name = payload.get("name")
    scopes = payload.get("scopes", [])
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name required")
    token = payload.get("token") or secrets.token_hex(32)
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO auth_tokens (name, token, scopes) VALUES ($1, $2, $3)",
            name,
            token,
            scopes,
        )
    return {"name": name, "token": token, "scopes": scopes}


__all__ = ["router"]
