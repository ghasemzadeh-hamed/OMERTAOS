"""Implementation of the ``aion apply`` command."""
from __future__ import annotations

import pathlib

import typer

from ..services.bundle import BundleService, BundleSettings


def register(app: typer.Typer) -> None:
    @app.command(
        "apply",
        help="Apply configuration bundles to the control plane",
        context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    )
    def apply_command(
        ctx: typer.Context,
        bundle: bool = typer.Option(
            False,
            "-b",
            "--bundle",
            help="Provide the bundle path as the next argument (aion apply --bundle <archive.tgz>).",
        ),
        atomic: bool = typer.Option(False, "--atomic", help="Rollback on failure."),
        no_browser: bool = typer.Option(
            False, "--no-browser", help="Skip browser based review before applying."
        ),
    ) -> None:
        extras = list(ctx.args)
        bundle_path: pathlib.Path | None = None
        if bundle:
            if not extras:
                raise typer.BadParameter("Expected a path immediately after --bundle", param_name="bundle")
            bundle_path = pathlib.Path(extras.pop(0))
        elif extras:
            bundle_path = pathlib.Path(extras.pop(0))
        if bundle_path is None:
            raise typer.BadParameter("--bundle <path.tgz> is required", param_name="bundle")
        if extras:
            raise typer.BadParameter(f"Unexpected arguments: {' '.join(extras)}")

        settings = BundleSettings(path=bundle_path, atomic=atomic, no_browser=no_browser)
        service = BundleService()
        report = service.apply(settings)
        typer.secho("Bundle applied", fg=typer.colors.GREEN)
        typer.echo(report)


__all__ = ["register"]
