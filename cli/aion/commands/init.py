"""Implementation of the ``aion init`` command group."""
from __future__ import annotations

import getpass
import sys
from typing import Optional

import typer

from ..services.quickstart import QuickstartOptions, QuickstartService


def _prompt_missing(options: QuickstartOptions) -> QuickstartOptions:
    if options.admin_email is None:
        options.admin_email = typer.prompt("Admin email")
    if options.admin_pass is None:
        options.admin_pass = getpass.getpass("Admin password: ")
    if not options.model:
        options.model = typer.prompt("Default model", default="gpt-4o-mini")
    return options


def register(app: typer.Typer) -> None:
    init_app = typer.Typer(help="Bootstrap a new AION OS deployment")

    @init_app.callback()
    def init_command(
        ctx: typer.Context,
        quickstart: bool = typer.Option(
            False, "--quickstart", help="Run the guided quickstart workflow."
        ),
        no_browser: bool = typer.Option(
            False, "--no-browser", help="Force headless mode even if a browser exists."
        ),
        admin_email: Optional[str] = typer.Option(
            None, "--admin-email", help="Seed admin email for the console."
        ),
        admin_pass: Optional[str] = typer.Option(
            None, "--admin-pass", help="Seed admin password for the console."
        ),
        provider: str = typer.Option(
            "local", "--provider", help="Default provider to configure (local|api|hybrid)."
        ),
        api_key: Optional[str] = typer.Option(
            None, "--api-key", help="API key when provider requires one."
        ),
        model: Optional[str] = typer.Option(
            None, "--model", help="Default model identifier to set up."
        ),
        port: int = typer.Option(3000, "--port", help="Port to bind the console to."),
    ) -> None:
        if not quickstart:
            typer.echo("Use --quickstart to launch the guided bootstrap workflow.")
            raise typer.Exit(code=1)

        options = QuickstartOptions(
            quickstart=quickstart,
            no_browser=no_browser,
            admin_email=admin_email,
            admin_pass=admin_pass,
            provider=provider,
            api_key=api_key,
            model=model,
            port=port,
            extra_args=list(ctx.args),
        )
        if options.no_browser or not sys.stdin.isatty():  # type: ignore[attr-defined]
            options = _prompt_missing(options)

        service = QuickstartService()
        result = service.run(options=options)
        typer.secho("Quickstart completed", fg=typer.colors.GREEN)
        for key, value in result.items():
            typer.echo(f"{key}: {value}")

    app.add_typer(init_app, name="init")


__all__ = ["register"]
