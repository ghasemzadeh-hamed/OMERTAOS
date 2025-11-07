"""FastAPI dependency helpers."""
from __future__ import annotations

from os.control.os.core.state import STATE, ControlState


def get_state() -> ControlState:
    return STATE
