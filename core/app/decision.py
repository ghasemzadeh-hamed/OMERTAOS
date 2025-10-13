from __future__ import annotations

import asyncio
import random
from typing import Any

from .schemas import ExecutionRoute, InferenceRequest, RouterDecision


class DecisionRouter:
    """Lightweight heuristic router used to prototype the architecture.

    In production this component would invoke an LLM and feed it telemetry about
    latency, cost, and module availability. For the prototype we rely on a few
    deterministic rules to keep the control flow predictable during tests.
    """

    def __init__(self, latency_budget_ms: int = 1200, local_token_limit: int = 512) -> None:
        self.latency_budget_ms = latency_budget_ms
        self.local_token_limit = local_token_limit

    async def route(self, request: InferenceRequest) -> RouterDecision:
        await asyncio.sleep(0)  # keep the method non-blocking for cooperative scheduling

        prompt_length = len(request.prompt)
        desired_latency = request.parameters.get("latency_budget_ms", self.latency_budget_ms)
        prefer_local = request.parameters.get("prefer_local", False)

        if prefer_local and prompt_length <= self.local_token_limit:
            return RouterDecision(route=ExecutionRoute.LOCAL, reason="Client requested local execution")

        if request.task_type in {"embedding", "tokenize"}:
            return RouterDecision(route=ExecutionRoute.LOCAL, reason="Task type serviced locally", model_hint="embeddings")

        if prompt_length <= self.local_token_limit and desired_latency < self.latency_budget_ms:
            return RouterDecision(route=ExecutionRoute.LOCAL, reason="Short prompt within latency budget")

        if request.task_type in {"summarize", "analyze"} and prompt_length > self.local_token_limit:
            return RouterDecision(route=ExecutionRoute.HYBRID, reason="Large analytical task routed to hybrid pipeline")

        # fallback to remote execution, optionally nudging model selection
        model_hint = random.choice(["gpt-4", "claude-3", "llama-3-70b"])
        return RouterDecision(route=ExecutionRoute.REMOTE, reason="Default remote execution", model_hint=model_hint)


async def get_router() -> DecisionRouter:
    return DecisionRouter()
