"""Authentication helpers for CLI commands."""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass

import typer


@dataclass
class AuthService:
    def issue_token(self, ttl: str, once: bool) -> str:
        seconds = self._parse_ttl(ttl)
        suffix = "once" if once else "multi"
        token = secrets.token_urlsafe(32)
        expiry = int(time.time()) + seconds
        typer.echo(f"[auth] issued {suffix}-use token valid for {seconds} seconds")
        return f"{token}:{expiry}:{suffix}"

    def _parse_ttl(self, ttl: str) -> int:
        ttl = ttl.strip().lower()
        if ttl.endswith("m"):
            return int(float(ttl[:-1]) * 60)
        if ttl.endswith("h"):
            return int(float(ttl[:-1]) * 3600)
        if ttl.endswith("s"):
            return int(float(ttl[:-1]))
        return int(ttl)
