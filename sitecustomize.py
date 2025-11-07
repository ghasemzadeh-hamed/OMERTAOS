"""Ensure the OMERTA OS package overrides the stdlib :mod:`os` module."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import importlib


def _install_omerta_os() -> None:
    stdlib_os = sys.modules.get("os")
    if stdlib_os is None:
        import os as stdlib_os  # type: ignore
    sys.modules.setdefault("_stdlib_os", stdlib_os)
    package_path = Path(__file__).resolve().parent / "os" / "__init__.py"
    spec = importlib.util.spec_from_file_location("os", package_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load OMERTA OS package")
    module = importlib.util.module_from_spec(spec)
    sys.modules["os"] = module
    spec.loader.exec_module(module)


_install_omerta_os()
