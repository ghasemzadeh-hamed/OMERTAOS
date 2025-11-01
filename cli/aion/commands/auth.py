"""Authentication helper commands for ``aion``."""
from __future__ import annotations

import typer

from ..services.auth import AuthService


def register(app: typer.Typer) -> None:
    auth_app = typer.Typer(help="Authentication helpers")

    @auth_app.command("token")
    def token(
        once: bool = typer.Option(False, "--once", help="Mark the token for single-use."),
        ttl: str = typer.Option("5m", "--ttl", help="Relative TTL, e.g. 5m or 1h."),
    ) -> None:
        service = AuthService()
        token_value = service.issue_token(ttl=ttl, once=once)
        typer.echo(token_value)

    app.add_typer(auth_app, name="auth")


__all__ = ["register"]
