import asyncio
import json
import logging
import time
from typing import Dict, Optional

from app.control.router import get_handler
from os.control.os.models import RouterDecision, Task, TaskStatus
from os.control.os.router_engine import decision_engine

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}

    def create_task(self, payload: Dict) -> Task:
        task = Task(
            schema_version=payload.get("schema_version", "1.0"),
            task_id=payload["task_id"],
            intent=payload["intent"],
            params=payload.get("params", {}),
            preferred_engine=payload.get("preferred_engine", "auto"),
            priority=payload.get("priority", "normal"),
            sla=payload.get("sla", {}),
            metadata=payload.get("metadata", {}),
            tenant_id=payload.get("tenant_id"),
        )
        self._tasks[task.task_id] = task
        return task

    async def execute(self, task: Task) -> Task:
        handler = get_handler(task.intent)
        if handler:
            task.engine_route = task.intent
            task.engine_reason = "intent_handler"
            task.engine_chosen_by = "router"
            task.engine_tier = "tier0"
            task.status = TaskStatus.RUNNING
            start = time.monotonic()
            events = []
            final_text = ""
            try:
                for event in handler({"task_id": task.task_id, "params": task.params}):
                    events.append(event)
                    if event.get("status") == "OK" and "text" in event:
                        final_text = str(event.get("text", ""))
                    if "delta" in event:
                        final_text = final_text + str(event["delta"])
                if not final_text and events:
                    final_text = str(events[-1].get("text", ""))
                latency_ms = (time.monotonic() - start) * 1000
                task.result = {
                    "agent": final_text,
                    "events": json.dumps(events, ensure_ascii=False),
                }
                task.status = TaskStatus.OK
                task.usage = {
                    "latency_ms": latency_ms,
                    "cost_usd": 0.0,
                    "tokens": len(final_text),
                }
            except Exception as exc:  # pragma: no cover - runtime dependent
                logger.exception("Agent handler failed", extra={"task_id": task.task_id, "intent": task.intent})
                task.status = TaskStatus.ERROR
                task.error = {"code": "AGENT_HANDLER_ERROR", "message": str(exc)}
                task.result = {"agent": "", "events": json.dumps(events, ensure_ascii=False)}
            cursor = f"{task.task_id}-final"
            task.stream_state.cursor = cursor
            task.stream_state.requires_ack = True
            task.stream_state.backpressure_hint = "ack-before-new-tasks"
            task.stream_state.retry_attempt = 0
            task.stream_state.max_attempts = 5
            task.stream_state.retry_after_ms = 250
            return task

        decision: RouterDecision = decision_engine.decide(task)
        task.engine_route = decision.route
        task.engine_reason = decision.reason
        task.engine_chosen_by = decision.chosen_by
        task.engine_tier = decision.tier
        task.status = TaskStatus.RUNNING
        await asyncio.sleep(0.1)
        start = time.monotonic()
        if decision.route == "local":
            await asyncio.sleep(0.05)
            task.result = {"summary": task.params.get("text", "").split(" ")[:10]}
        elif decision.route == "hybrid":
            await asyncio.sleep(0.05)
            task.result = {"hybrid": True, "tokens": len(str(task.params))}
        else:
            await asyncio.sleep(0.05)
            task.result = {"provider": "api", "response": "ok"}
        latency_ms = (time.monotonic() - start) * 1000
        task.status = TaskStatus.OK
        task.usage = {
            "latency_ms": latency_ms,
            "cost_usd": min(task.sla.get("budget_usd", 0.02), 0.2),
            "tokens": len(str(task.result)),
        }
        cursor = f"{task.task_id}-final"
        task.stream_state.cursor = cursor
        task.stream_state.requires_ack = True
        task.stream_state.backpressure_hint = "ack-before-new-tasks"
        task.stream_state.retry_attempt = 0
        task.stream_state.max_attempts = 5
        task.stream_state.retry_after_ms = 250
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def acknowledge_stream(self, task_id: str, cursor: str, consumer_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.stream_state.cursor != cursor:
            return False
        task.stream_state.mark_acked(consumer_id)
        task.stream_state.requires_ack = False
        return True


orchestrator = Orchestrator()
