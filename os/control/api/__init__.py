
"""Compatibility shim for ``os.control.os.api.__init__``."""
from __future__ import annotations

from importlib import import_module as _import_module

_target = _import_module('os.control.os.api.__init__')
_globals = globals()
for _name in getattr(_target, '__all__', [n for n in dir(_target) if not n.startswith('_')]):
    _globals[_name] = getattr(_target, _name)
__all__ = getattr(_target, '__all__', [n for n in _globals if not n.startswith('_')])
if hasattr(_target, '__path__'):
    __path__ = _target.__path__  # type: ignore[assignment]
if hasattr(_target, '__spec__'):
    __spec__ = _target.__spec__
