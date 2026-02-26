from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TaskNode:
    id: str
    deps: set[str] = field(default_factory=set)


class Dag:
    def __init__(self) -> None:
        self.nodes: dict[str, TaskNode] = {}

    def add(self, node: TaskNode) -> None:
        self.nodes[node.id] = node

    def topological(self) -> list[str]:
        pending = {k: set(v.deps) for k, v in self.nodes.items()}
        ordered: list[str] = []
        while pending:
            ready = sorted([n for n, deps in pending.items() if not deps])
            if not ready:
                raise ValueError("cycle detected")
            ordered.extend(ready)
            for r in ready:
                pending.pop(r)
            for deps in pending.values():
                deps.difference_update(ready)
        return ordered
