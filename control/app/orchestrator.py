import asyncio
import time
from typing import Dict, Optional

from .models import RouterDecision, Task, TaskStatus
from .router_engine import decision_engine


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
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)


orchestrator = Orchestrator()
