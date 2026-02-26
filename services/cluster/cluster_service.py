from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClusterNode:
    node_id: str
    mode: str


class ClusterService:
    def __init__(self) -> None:
        self._nodes: dict[str, ClusterNode] = {}

    def register_node(self, node_id: str, mode: str = "local") -> ClusterNode:
        node = ClusterNode(node_id=node_id, mode=mode)
        self._nodes[node_id] = node
        return node

    def list_nodes(self) -> list[ClusterNode]:
        return list(self._nodes.values())

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": "cluster"}
