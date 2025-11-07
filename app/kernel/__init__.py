"""Canonical import location for the AION-OS kernel runtime."""

from __future__ import annotations

import importlib
import sys

_module = importlib.import_module("os.kernel")
sys.modules[__name__] = _module

globals().update({k: v for k, v in vars(_module).items() if k not in globals()})

__all__ = getattr(_module, "__all__", [])
