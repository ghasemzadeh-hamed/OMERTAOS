"""Governance hooks for runtime auditing and traceability."""
from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

EventSink = Callable[[Dict[str, Any]], None]


class GovernanceHook:
    """Records routing and execution decisions for compliance."""

    def __init__(self, sinks: Optional[List[EventSink]] = None) -> None:
        self._logger = logging.getLogger("kernel.governance")
        self._events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._sinks = list(sinks or [])

    def register_sink(self, sink: EventSink) -> None:
        with self._lock:
            self._sinks.append(sink)

    def record_decision(self, intent: str, context: Dict[str, Any]) -> None:
        """Persist a governance event in memory and logs."""
        event = {
            "intent": intent,
            "context": self._mask(context),
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        payload = json.dumps(event, sort_keys=True)
        with self._lock:
            self._events.append(event)
            for sink in self._sinks:
                try:
                    sink(event)
                except Exception as exc:  # pragma: no cover - sink failure should not crash kernel
                    self._logger.warning("governance_sink_failed", extra={"error": str(exc)})
        self._logger.info("governance_event", extra={"payload": payload})

    def middleware(self, intent: str, handler: Callable[[Dict[str, Any]], Any]) -> Callable[[Dict[str, Any]], Any]:
        """Wrap a handler with policy logging around execution."""

        def wrapped(payload: Dict[str, Any]) -> Any:
            event = {"intent": intent, "payload": self._mask(payload)}
            self.record_decision(intent=intent, context=event)
            return handler(payload)

        return wrapped

    def list_events(self) -> List[Dict[str, Any]]:
        """Return a copy of the recorded events."""
        with self._lock:
            return list(self._events)

    def _mask(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        redacted: Dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in {"token", "secret", "password", "credential"}:
                redacted[key] = "***"
            else:
                redacted[key] = value
        return redacted


__all__ = ["GovernanceHook"]
