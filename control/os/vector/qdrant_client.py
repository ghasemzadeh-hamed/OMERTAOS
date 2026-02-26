"""Compatibility shim for ``data.vector.qdrant_client``."""
from __future__ import annotations

from data.vector.qdrant_client import *  # noqa: F403
from data.vector.qdrant_client import __all__ as _all

__all__ = list(_all)
