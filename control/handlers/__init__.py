"""Intent handlers for control plane task execution."""

from __future__ import annotations

from typing import Callable, Dict, Iterable

from app.control.handlers.agent_chat import handle_agent_chat

Handler = Callable[[dict], Iterable[dict]]

HANDLERS: Dict[str, Handler] = {
    "agent.chat": handle_agent_chat,
}

__all__ = ["Handler", "HANDLERS", "handle_agent_chat"]
