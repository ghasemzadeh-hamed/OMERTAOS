
"""Compatibility proxy to the relocated ``os.control.os.vector`` package."""
from __future__ import annotations

from importlib import import_module as _import_module

_proxy = _import_module("os.control.os.vector")
__all__ = getattr(_proxy, "__all__", [name for name in dir(_proxy) if not name.startswith("_")])
__path__ = getattr(_proxy, "__path__", [])  # type: ignore[assignment]
__spec__ = getattr(_proxy, "__spec__", None)
if __spec__ is not None:
    __spec__.submodule_search_locations = getattr(__spec__, "submodule_search_locations", __path__)


def __getattr__(name: str):  # pragma: no cover - thin proxy
    return getattr(_proxy, name)


def __dir__() -> list[str]:  # pragma: no cover - thin proxy
    return sorted(set(__all__))
