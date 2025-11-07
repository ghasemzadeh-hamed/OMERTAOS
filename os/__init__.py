"""Compatibility shim for exposing the Python stdlib ``os`` module while
also providing access to the OMERTA OS package."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from typing import List

_stdlib_os: ModuleType | None = sys.modules.get("_stdlib_os")
if _stdlib_os is None:  # pragma: no cover - defensive fallback
    raise ImportError("Standard library 'os' module must be preloaded")

__all__: List[str] = []

_reserved = {
    "__builtins__",
    "__doc__",
    "__loader__",
    "__name__",
    "__package__",
    "__spec__",
    "__file__",
    "__cached__",
}

for attr, value in vars(_stdlib_os).items():
    if attr in _reserved:
        continue
    globals().setdefault(attr, value)

stdlib_all = getattr(_stdlib_os, "__all__", [])
if stdlib_all:
    __all__.extend(name for name in stdlib_all if name not in __all__)

package_dir = globals().get("__file__")
if isinstance(package_dir, str):
    if "/" in package_dir:
        __path__ = [package_dir.rsplit("/", 1)[0]]  # type: ignore[assignment]
    elif "\\" in package_dir:
        __path__ = [package_dir.rsplit("\\", 1)[0]]  # type: ignore[assignment]
    else:
        __path__ = ["."]  # type: ignore[assignment]
    spec = globals().get("__spec__")
    if spec is not None:
        spec.submodule_search_locations = list(__path__)  # type: ignore[attr-defined]

for extra in ("control", "kernel", "config", "main"):
    if extra not in __all__:
        __all__.append(extra)

if hasattr(_stdlib_os, "path"):
    sys.modules.setdefault("os.path", getattr(_stdlib_os, "path"))

_alias_targets = {"config": "os.control.config", "main": "os.control.main"}


def __getattr__(name: str):  # pragma: no cover - lazy loader
    target = _alias_targets.get(name)
    if target is None:
        raise AttributeError(name)
    module = importlib.import_module(target)
    globals()[name] = module
    sys.modules.setdefault(f"os.{name}", module)
    if name not in __all__:
        __all__.append(name)
    return module
