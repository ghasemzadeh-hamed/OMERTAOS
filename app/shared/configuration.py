"""Helpers for locating configuration assets shipped with the repository."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIRNAME = "config"
PROFILES_SUBDIR = "profiles"
TEMPLATES_SUBDIR = "templates"


def get_config_root(root: Path | None = None) -> Path:
    base = Path(root) if root else REPO_ROOT
    return base / CONFIG_DIRNAME


def get_profiles_dir(root: Path | None = None) -> Path:
    return get_config_root(root) / PROFILES_SUBDIR


def get_templates_dir(root: Path | None = None) -> Path:
    return get_config_root(root) / TEMPLATES_SUBDIR


def ensure_config_dirs(root: Path | None = None) -> None:
    for directory in _iter_directories(root):
        directory.mkdir(parents=True, exist_ok=True)


def _iter_directories(root: Path | None = None) -> Iterable[Path]:
    base = get_config_root(root)
    yield base
    yield base / PROFILES_SUBDIR
    yield base / TEMPLATES_SUBDIR


def load_env_template(root: Path | None = None, *, filename: str = ".env.example") -> str:
    template_path = get_templates_dir(root) / filename
    return template_path.read_text(encoding="utf-8")


def write_env_file(content: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
