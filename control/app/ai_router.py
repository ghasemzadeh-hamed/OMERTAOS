import asyncio
import json
from typing import Any, Dict

import grpc
import httpx
import structlog
from redis.asyncio import Redis
from tenacity import retry, stop_after_attempt, wait_fixed

from .models import ActivityLog, Task
from .schemas import RouterDecision, RouterResponse, TaskCreate
from .settings import settings
from .protos import aion_pb2, aion_pb2_grpc

logger = structlog.get_logger(__name__)


class AIRouter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def decide(self, task: TaskCreate) -> RouterDecision:
        if settings.openai_api_key:
            try:
                decision = await self._decide_with_openai(task)
                return decision
            except Exception as exc:  # pragma: no cover - fallback path
                logger.warning("openai decision failed", error=str(exc))
        return self._heuristic_decision(task)

    async def _decide_with_openai(self, task: TaskCreate) -> RouterDecision:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        system_prompt = (
            "Decide optimal execution route: local, api, or hybrid → output {decision, reason}."
        )
        response = await client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": json.dumps(task.model_dump()),
                },
            ],
            temperature=0,
        )
        text = response.output[0].content[0].text
        parsed = json.loads(text)
        return RouterDecision(decision=parsed.get("decision", "local"), reason=parsed.get("reason", "heuristic"))

    def _heuristic_decision(self, task: TaskCreate) -> RouterDecision:
        intent = task.intent.lower()
        if 'realtime' in intent or task.priority >= 4:
            decision = 'local'
            reason = 'High priority tasks executed locally'
        elif 'embedding' in intent or 'vector' in intent:
            decision = 'hybrid'
            reason = 'Vector workloads benefit from hybrid pipeline'
        else:
            decision = task.preferred_engine or 'api'
            reason = 'Default to external API'
        return RouterDecision(decision=decision, reason=reason)

    async def execute(self, task: Task, payload: TaskCreate) -> RouterResponse:
        decision = await self.decide(payload)
        result: Dict[str, Any]
        if decision.decision == 'local':
            result = await self._call_execution(task)
        elif decision.decision == 'hybrid':
            local = await self._call_execution(task)
            remote = await self._call_external(payload)
            result = {'local': local, 'remote': remote}
        else:
            result = await self._call_external(payload)
        return RouterResponse(decision=decision, output=result)

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(3))
    async def _call_execution(self, task: Task) -> Dict[str, Any]:
        async with grpc.aio.insecure_channel(settings.execution_endpoint.replace('http://', '')) as channel:
            stub = aion_pb2_grpc.TaskExecutorStub(channel)
            request = aion_pb2.TaskRequest(
                external_id=task.external_id,
                intent=task.intent,
                payload=json.dumps(task.params),
            )
            response = await stub.ExecuteTask(request)
            return {
                'external_id': response.external_id,
                'status': response.status,
                'output': json.loads(response.output or '{}'),
            }

    async def _call_external(self, payload: TaskCreate) -> Dict[str, Any]:
        if settings.ollama_url:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{settings.ollama_url}/api/generate",
                    json={"model": "llama3", "prompt": json.dumps(payload.model_dump())},
                )
                if response.status_code == 200:
                    data = response.json()
                    return {'engine': 'ollama', 'response': data.get('response')}
        return {'engine': 'mock', 'response': f"Processed {payload.intent}"}

    async def record_activity(self, session, task: Task, action: str, payload: Dict[str, Any]) -> None:
        log = ActivityLog(task_id=task.id, action=action, payload=payload)
        session.add(log)
        await session.commit()
        await session.refresh(log)
        await self.redis.publish('tasks:updates', json.dumps({'task_id': task.external_id, 'action': action, 'payload': payload}))


async def get_router(redis: Redis) -> AIRouter:
    return AIRouter(redis)
