"""Bundle application workflow for ``aion apply``."""
from __future__ import annotations

import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

import typer

from .schemas import BundleValidator


@dataclass
class BundleSettings:
    path: Path
    atomic: bool
    no_browser: bool


class BundleService:
    """Apply config bundles and validate against JSON Schemas."""

    def __init__(self) -> None:
        self.validator = BundleValidator()

    def apply(self, settings: BundleSettings) -> str:
        if not settings.path.exists():
            raise typer.BadParameter(f"bundle {settings.path} does not exist")
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._extract(settings.path, Path(tmp_dir))
            validation_report = self.validator.validate_bundle(Path(tmp_dir))
            self._install_services(Path(tmp_dir) / "services")
        summary = ["Bundle validation report:"] + [f"- {item}" for item in validation_report]
        if settings.atomic:
            summary.append("Atomic mode is simulated (no rollback performed in stub).")
        return "\n".join(summary)

    def _extract(self, archive: Path, destination: Path) -> None:
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(destination)

    def _install_services(self, service_dir: Path) -> None:
        if not service_dir.exists():
            typer.echo("[apply] no systemd units found in bundle")
            return
        for service_file in sorted(service_dir.glob("*.service")):
            typer.echo(f"[apply] would install systemd unit {service_file.name}")
