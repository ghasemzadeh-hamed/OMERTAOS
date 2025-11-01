"""Terminal UI launcher commands."""
from __future__ import annotations

import typer

from ..services.tui import TuiServerService


def register(app: typer.Typer) -> None:
    tui_app = typer.Typer(help="Serve the terminal explorer UI")

    @tui_app.command("serve")
    def serve(
        port: int = typer.Option(3030, "--port", help="Port to bind the explorer server to."),
        api: str = typer.Option("http://127.0.0.1:8001", "--api", help="Control API base URL."),
        token: str = typer.Option(..., "--token", help="Authentication token to forward."),
    ) -> None:
        service = TuiServerService(port=port, api_url=api, token=token)
        service.run()

    app.add_typer(tui_app, name="tui-serve")


__all__ = ["register"]
