"""Compatibility package re-exporting control plugins from :mod:`os.control.aionos_control`."""

from __future__ import annotations

import os.control.aionos_control as _impl
from os.control.aionos_control import *  # type: ignore[F401,F403]

__all__ = getattr(_impl, "__all__", [])
