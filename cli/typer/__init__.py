"""Proxy module to expose the repository Typer shim when CLI is on ``sys.path``."""

from __future__ import annotations

import sys
from importlib import util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHIM_PATH = ROOT / "typer" / "__init__.py"

spec = util.spec_from_file_location("_aion_typer_shim", SHIM_PATH)
if spec is None or spec.loader is None:  # pragma: no cover - defensive guard
    raise ImportError("Unable to locate typer shim at repository root")

module = util.module_from_spec(spec)
sys.modules.setdefault("_aion_typer_shim", module)
spec.loader.exec_module(module)

for name in getattr(module, "__all__", []):
    globals()[name] = getattr(module, name)

__all__ = getattr(module, "__all__", [])
