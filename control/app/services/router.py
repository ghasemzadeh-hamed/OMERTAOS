from __future__ import annotations

import json

import httpx

from ..config import get_settings
from ..schemas import TaskCreate, TaskRouteDecision

settings = get_settings()


async def call_llm(task: TaskCreate) -> TaskRouteDecision | None:
    if not settings.openai_api_key:
        return None

    system_prompt = (
        "Given this task JSON, decide optimal execution route: local, api, or hybrid. "
        "Output pure JSON {decision, reason}."
    )
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {settings.openai_api_key}'},
            json={
                'model': settings.router_model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': json.dumps(task.model_dump(by_alias=True))},
                ],
                'temperature': 0
            }
        )
        response.raise_for_status()
        content = response.json()
        message = content['choices'][0]['message']['content']
        data = json.loads(message)
        return TaskRouteDecision(**data)


def heuristic_decision(task: TaskCreate) -> TaskRouteDecision:
    if task.preferred_engine:
        return TaskRouteDecision(decision=task.preferred_engine, reason='User preference')
    if task.intent.lower().startswith('summarize'):
        return TaskRouteDecision(decision='local', reason='Summarization handled locally')
    if task.intent.lower().startswith('analyze'):
        return TaskRouteDecision(decision='hybrid', reason='Analysis benefits from hybrid pipeline')
    return TaskRouteDecision(decision='api', reason='Default to API execution')


async def decide_route(task: TaskCreate) -> TaskRouteDecision:
    llm_decision = await call_llm(task)
    if llm_decision:
        return llm_decision
    return heuristic_decision(task)
