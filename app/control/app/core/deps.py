"""FastAPI dependency helpers."""
from __future__ import annotations

from app.control.app.core.state import STATE, ControlState


def get_state() -> ControlState:
    return STATE
