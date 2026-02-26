from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from kernel.isolation import CpuManager, GpuManager, MemoryManager
from kernel.multitenant.execution_context import ExecutionContext
from kernel.runtime import ModelRuntime


@dataclass(frozen=True)
class AgentNode:
    agent_id: str
    model_id: str
    dependencies: tuple[str, ...] = tuple()
    payload: dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    def __init__(self, cpu: CpuManager, memory: MemoryManager, gpu: GpuManager) -> None:
        self._cpu = cpu
        self._memory = memory
        self._gpu = gpu

    def topo_sort(self, nodes: list[AgentNode]) -> list[AgentNode]:
        by_id = {n.agent_id: n for n in nodes}
        indeg: dict[str, int] = {n.agent_id: 0 for n in nodes}
        graph: dict[str, list[str]] = defaultdict(list)
        for node in nodes:
            for dep in node.dependencies:
                graph[dep].append(node.agent_id)
                indeg[node.agent_id] += 1
        q = deque([nid for nid, deg in indeg.items() if deg == 0])
        order: list[AgentNode] = []
        while q:
            cur = q.popleft()
            order.append(by_id[cur])
            for nxt in graph[cur]:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    q.append(nxt)
        if len(order) != len(nodes):
            raise ValueError("orchestration DAG cycle detected")
        return order

    def dispatch(self, context: ExecutionContext, nodes: list[AgentNode], profile: str) -> list[dict[str, Any]]:
        outputs: list[dict[str, Any]] = []
        for node in self.topo_sort(nodes):
            self._cpu.allocate(context.tenant_id, node.agent_id, profile)
            self._memory.allocate(context.tenant_id, node.agent_id, profile)
            gpu = self._gpu.allocate(context.tenant_id, node.agent_id, profile)
            runtime = ModelRuntime(model_id=node.model_id, provider="default")
            result = runtime.infer(prompt=node.payload.get("prompt", ""), agent_id=node.agent_id, gpu=gpu.devices)
            outputs.append({"agent_id": node.agent_id, "result": result})
        return outputs
