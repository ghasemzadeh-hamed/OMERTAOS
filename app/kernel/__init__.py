"""Canonical import location for the AION-OS kernel runtime."""

from __future__ import annotations

from importlib import import_module
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_os_kernel = import_module("os.kernel")

for _name in dir(_os_kernel):
    if _name.startswith("_"):
        continue
    globals().setdefault(_name, getattr(_os_kernel, _name))

__all__ = list(getattr(_os_kernel, "__all__", []))
