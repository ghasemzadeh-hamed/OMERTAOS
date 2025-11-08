"""Canonical package for the AION-OS control plane.

This package re-exports the existing implementation that lives under
``os.control`` so callers can depend on the new ``app.control`` import
path without breaking older entrypoints.  The indirection keeps the
refactor incremental while we migrate the rest of the codebase.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

_module = importlib.import_module("os.control")

# Ensure both ``os.control`` and ``app.control`` submodules can be resolved.
if hasattr(_module, "__path__"):
    current_dir = str(Path(__file__).resolve().parent)
    search_path = list(_module.__path__)  # type: ignore[attr-defined]
    if current_dir not in search_path:
        search_path.append(current_dir)
        _module.__path__ = type(_module.__path__)(search_path)  # type: ignore[assignment]

sys.modules[__name__] = _module

# Populate module globals for static analyzers and introspection tools.
globals().update({k: v for k, v in vars(_module).items() if k not in globals()})

__all__ = getattr(_module, "__all__", [])
