"""Agent lifecycle management primitives."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from .context_manager import ContextManager
from .task_queue import Task, TaskQueue


class AgentState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass
class AgentRecord:
    agent_id: str
    state: AgentState
    metadata: Dict[str, object]


class TelemetryEmitter:
    """Emit lifecycle telemetry events."""

    def emit(self, event: str, payload: Dict[str, object]) -> None:  # pragma: no cover - extension hook
        print(f"telemetry::{event}::{payload}")


class AgentLifecycle:
    """Coordinates agent state changes and orchestration hooks."""

    def __init__(self, queue: TaskQueue, contexts: ContextManager, telemetry: Optional[TelemetryEmitter] = None) -> None:
        self._queue = queue
        self._contexts = contexts
        self._telemetry = telemetry or TelemetryEmitter()
        self._agents: Dict[str, AgentRecord] = {}

    def register(self, agent_id: str, metadata: Dict[str, object] | None = None) -> AgentRecord:
        record = AgentRecord(agent_id=agent_id, state=AgentState.CREATED, metadata=metadata or {})
        self._agents[agent_id] = record
        self._telemetry.emit("agent_registered", {"agent_id": agent_id})
        return record

    def start(self, agent_id: str, session_id: str, user_id: str) -> AgentRecord:
        record = self._agents[agent_id]
        self._contexts.create(session_id=session_id, user_id=user_id)
        record.state = AgentState.RUNNING
        self._queue.submit(
            Task(
                task_id=f"bootstrap-{agent_id}",
                payload={"agent_id": agent_id, "session_id": session_id},
                priority=1,
            )
        )
        self._telemetry.emit("agent_started", {"agent_id": agent_id, "session_id": session_id})
        return record

    def stop(self, agent_id: str, session_id: str) -> AgentRecord:
        record = self._agents[agent_id]
        record.state = AgentState.STOPPED
        self._contexts.delete(session_id=session_id)
        self._queue.submit(
            Task(
                task_id=f"teardown-{agent_id}",
                payload={"agent_id": agent_id, "session_id": session_id},
                priority=2,
            )
        )
        self._telemetry.emit("agent_stopped", {"agent_id": agent_id, "session_id": session_id})
        return record


__all__ = ["AgentLifecycle", "AgentRecord", "AgentState", "TelemetryEmitter"]
