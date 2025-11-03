"""Local (personal mode) management commands for the AION CLI."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable

import typer

_local_app = typer.Typer(help="Manage the personal (local) AION-OS stack and templates.")

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_COMPOSE_FILE = ROOT_DIR / "docker-compose.local.yml"
TEMPLATE_DIR = ROOT_DIR / "agents" / "templates"


def register(app: typer.Typer) -> None:
    """Register the ``local`` command group with the top-level CLI."""

    app.add_typer(_local_app, name="local")


def _ensure_docker() -> str:
    docker = shutil.which("docker")
    if docker is None:
        typer.secho(
            "docker command not found; please install Docker Desktop or CLI",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    return docker


def _compose(compose_file: Path, args: Iterable[str]) -> None:
    docker = _ensure_docker()
    if not compose_file.exists():
        typer.secho(f"compose file not found: {compose_file}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    command = [docker, "compose", "-f", str(compose_file), *args]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - passthrough
        raise typer.Exit(exc.returncode) from exc


@_local_app.command("start")
def start(
    compose_file: Path = typer.Option(
        DEFAULT_COMPOSE_FILE,
        "--compose-file",
        "-f",
        file_okay=True,
        dir_okay=False,
        help="Path to the docker compose file for personal mode.",
    ),
    build: bool = typer.Option(
        True,
        "--build/--no-build",
        help="Whether to build container images before starting.",
    ),
) -> None:
    """Start the personal mode stack."""

    args = ["up", "-d"]
    if build:
        args.append("--build")
    _compose(compose_file, args)
    typer.echo("Local stack is running. Access the console at http://localhost:3000")


@_local_app.command("stop")
def stop(
    compose_file: Path = typer.Option(
        DEFAULT_COMPOSE_FILE,
        "--compose-file",
        "-f",
        file_okay=True,
        dir_okay=False,
        help="Path to the docker compose file for personal mode.",
    ),
    prune: bool = typer.Option(
        False,
        "--prune/--no-prune",
        help="Remove named volumes (data) after stopping.",
    ),
) -> None:
    """Stop the personal mode stack."""

    args = ["down"]
    if prune:
        args.append("--volumes")
    _compose(compose_file, args)
    typer.echo("Local stack stopped.")


@_local_app.command("status")
def status(
    compose_file: Path = typer.Option(
        DEFAULT_COMPOSE_FILE,
        "--compose-file",
        "-f",
        file_okay=True,
        dir_okay=False,
        help="Path to the docker compose file for personal mode.",
    ),
) -> None:
    """Show docker compose status for personal mode."""

    _compose(compose_file, ["ps"])


@_local_app.command("templates")
def templates(
    show_contents: bool = typer.Option(
        False,
        "--show/--no-show",
        help="Print the YAML content of each template.",
    )
) -> None:
    """List available agent templates for personal mode."""

    if not TEMPLATE_DIR.exists():
        typer.secho(
            "no agent templates found; run upgrade or sync the repository",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    files = sorted(p for p in TEMPLATE_DIR.glob("*.agent.y*ml") if p.is_file())
    if not files:
        typer.secho("no agent templates available", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    typer.echo("Available agent templates:\n")
    for template in files:
        typer.echo(f"- {template.name}")
        if show_contents:
            typer.echo("".join(["\n", template.read_text(encoding="utf-8"), "\n"]))


@_local_app.command("install")
def install_personal() -> None:
    """Run the bash installer in personal mode (requires bash)."""

    installer = ROOT_DIR / "install.sh"
    if not installer.exists():
        typer.secho("install.sh not found in repository root", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    command = ["bash", str(installer), "--local"]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - passthrough
        raise typer.Exit(exc.returncode) from exc
