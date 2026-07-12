from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TaskNode:
    id: str
    deps: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("task node id is required")
        normalized = frozenset(dep.strip() for dep in self.deps if dep.strip())
        if self.id in normalized:
            raise ValueError(f"task node {self.id!r} cannot depend on itself")
        object.__setattr__(self, "deps", normalized)


class Dag:
    """Deterministic in-memory DAG primitive owned by Control."""

    def __init__(self) -> None:
        self.nodes: dict[str, TaskNode] = {}

    def add(self, node: TaskNode) -> None:
        if node.id in self.nodes:
            raise ValueError(f"duplicate task node: {node.id}")
        self.nodes[node.id] = node

    def topological(self) -> list[str]:
        known = set(self.nodes)
        missing = sorted({dep for node in self.nodes.values() for dep in node.deps if dep not in known})
        if missing:
            raise ValueError("unknown task dependencies: " + ", ".join(missing))

        pending = {node_id: set(node.deps) for node_id, node in self.nodes.items()}
        ordered: list[str] = []
        while pending:
            ready = sorted(node_id for node_id, deps in pending.items() if not deps)
            if not ready:
                raise ValueError("cycle detected")
            ordered.extend(ready)
            for node_id in ready:
                pending.pop(node_id)
            for deps in pending.values():
                deps.difference_update(ready)
        return ordered
