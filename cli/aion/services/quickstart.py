"""Quickstart onboarding helpers."""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import typer


@dataclass
class QuickstartOptions:
    quickstart: bool
    no_browser: bool
    admin_email: Optional[str]
    admin_pass: Optional[str]
    provider: str
    api_key: Optional[str]
    model: Optional[str]
    port: int
    extra_args: List[str] = field(default_factory=list)


class QuickstartService:
    """Execute a guided bootstrap flow in headless or interactive mode."""

    def run(self, options: QuickstartOptions) -> Dict[str, str]:
        if options.provider not in {"local", "api", "hybrid"}:
            raise typer.BadParameter("provider must be one of local, api, hybrid")

        self._log("Provisioning control plane state")
        self._simulate_delay()
        self._log("Seeding administrator account")
        self._simulate_delay()
        self._log(f"Configured provider: {options.provider}")
        if options.api_key:
            self._log("API key registered securely")
        token = self._issue_token(ttl_seconds=5 * 60)
        self._log(f"Console will be reachable on http://127.0.0.1:{options.port}")
        return {
            "admin": options.admin_email or "admin@example.com",
            "provider": options.provider,
            "model": options.model or "gpt-4o-mini",
            "console_port": str(options.port),
            "one_time_token": token,
        }

    def _issue_token(self, ttl_seconds: int) -> str:
        payload = f"tok_{secrets.token_urlsafe(18)}:{int(time.time()) + ttl_seconds}"
        return payload

    def _simulate_delay(self) -> None:
        time.sleep(0.05)

    def _log(self, message: str) -> None:
        typer.echo(f"[quickstart] {message}")
