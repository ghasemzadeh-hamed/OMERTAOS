"""Intent router for control plane handlers."""

from __future__ import annotations

from app.control.handlers import HANDLERS, Handler


def get_handler(intent: str) -> Handler | None:
    """Return the handler registered for the given intent."""

    return HANDLERS.get(intent)


__all__ = ["get_handler", "HANDLERS", "Handler"]
