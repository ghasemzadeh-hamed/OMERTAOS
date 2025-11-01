"""System diagnostics via ``aion doctor``."""
from __future__ import annotations

import typer

from ..services.doctor import DoctorService


def register(app: typer.Typer) -> None:
    @app.command("doctor", help="Run health diagnostics against the control API")
    def doctor_command(
        verbose: bool = typer.Option(False, "--verbose", help="Verbose output."),
    ) -> None:
        service = DoctorService(verbose=verbose)
        ok, report = service.run()
        if ok:
            typer.secho("All systems healthy", fg=typer.colors.GREEN)
        else:
            typer.secho("Issues detected", fg=typer.colors.RED)
        typer.echo(report)
        raise typer.Exit(code=0 if ok else 1)


__all__ = ["register"]
