"""Implementation of the ``aion apply`` command group."""
from __future__ import annotations

import pathlib

import typer

from ..services.bundle import BundleService, BundleSettings


def register(app: typer.Typer) -> None:
    apply_app = typer.Typer(help="Apply configuration bundles to the control plane")

    @apply_app.command()
    def bundle(
        path: pathlib.Path = typer.Argument(..., help="Path to the bundle .tgz archive."),
        atomic: bool = typer.Option(False, "--atomic", help="Rollback on failure."),
        no_browser: bool = typer.Option(
            False, "--no-browser", help="Skip browser based review before applying."
        ),
    ) -> None:
        """Apply a configuration bundle."""

        settings = BundleSettings(path=path, atomic=atomic, no_browser=no_browser)
        service = BundleService()
        report = service.apply(settings)
        typer.secho("Bundle applied", fg=typer.colors.GREEN)
        typer.echo(report)

    app.add_typer(apply_app, name="apply")


__all__ = ["register"]
