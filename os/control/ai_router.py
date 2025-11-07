
"""Compatibility shim for ``os.control.os.ai_router``."""
from __future__ import annotations

from importlib import import_module as _import_module

_target = _import_module('os.control.os.ai_router')
_globals = globals()
for _name in getattr(_target, '__all__', [n for n in dir(_target) if not n.startswith('_')]):
    _globals[_name] = getattr(_target, _name)
__all__ = getattr(_target, '__all__', [n for n in _globals if not n.startswith('_')])
