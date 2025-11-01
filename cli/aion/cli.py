"""Entrypoint for the ``aion`` Typer-based CLI."""
from __future__ import annotations

import importlib
import sys
from typing import Optional

import typer

app = typer.Typer(help="AION Operating System command line interface.")


# Dynamically register command groups to keep startup fast when optional
# dependencies such as Textual or FastAPI are missing.  Each module defines a
# ``register`` function that takes the root Typer app.
for module_name in (
    "aion.commands.init",
    "aion.commands.apply",
    "aion.commands.doctor",
    "aion.commands.auth",
    "aion.commands.tui",
):
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:  # pragma: no cover - guard for packaging issues
        typer.echo(f"warning: failed to import {module_name}: {exc}", err=True)
        continue

    register = getattr(module, "register", None)
    if register is None:
        typer.echo(
            f"warning: module {module_name} does not expose a register(app) function",
            err=True,
        )
        continue
    register(app)


def main(argv: Optional[list[str]] = None) -> None:
    """Execute the Typer application."""

    app(args=argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover
    main()
