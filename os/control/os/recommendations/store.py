"""In-memory store for tool/resource recommendations (latentbox-backed)."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence


@dataclass
class ToolResourceRecord:
    """Persistent representation of an external tool/resource."""

    id: str
    name: str
    category: str
    url: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    source: str = "latentbox"
    scenarios: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())


class ToolResourceStore:
    """Thread-safe container for tool resources and recommendations."""

    def __init__(self) -> None:
        self._records: Dict[str, ToolResourceRecord] = {}
        self._lock = asyncio.Lock()

    def seed(self, resources: Iterable[ToolResourceRecord]) -> None:
        for resource in resources:
            self._records[resource.id] = resource

    async def upsert_many(self, resources: Sequence[ToolResourceRecord]) -> List[ToolResourceRecord]:
        async with self._lock:
            stored: List[ToolResourceRecord] = []
            now = time.time()
            for resource in resources:
                existing = self._records.get(resource.id)
                if existing:
                    existing.name = resource.name
                    existing.category = resource.category
                    existing.url = resource.url
                    existing.description = resource.description
                    existing.tags = list(resource.tags)
                    existing.source = resource.source
                    existing.scenarios = list(resource.scenarios)
                    existing.capabilities = list(resource.capabilities)
                    existing.constraints = list(resource.constraints)
                    existing.updated_at = now
                    stored.append(existing)
                else:
                    resource.created_at = now
                    resource.updated_at = now
                    self._records[resource.id] = resource
                    stored.append(resource)
            return stored

    async def list(
        self,
        *,
        source: Optional[str] = None,
        categories: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
    ) -> List[ToolResourceRecord]:
        async with self._lock:
            resources = list(self._records.values())
        if source:
            resources = [r for r in resources if r.source == source]
        if categories:
            category_set = set(categories)
            resources = [r for r in resources if r.category in category_set]
        if tags:
            tag_set = set(tags)
            resources = [r for r in resources if tag_set.intersection(set(r.tags))]
        return resources

    async def recommend(
        self,
        *,
        source: Optional[str] = None,
        scenario: Optional[str] = None,
        capabilities: Optional[Sequence[str]] = None,
        constraints: Optional[Sequence[str]] = None,
    ) -> List[ToolResourceRecord]:
        resources = await self.list(source=source)
        scores: List[tuple[float, ToolResourceRecord]] = []
        capability_set = set(capabilities or [])
        constraint_set = set(constraints or [])
        for resource in resources:
            score = 0.0
            if scenario and scenario in resource.scenarios:
                score += 2.0
            if capability_set and capability_set.intersection(resource.capabilities):
                score += 1.5
            if constraint_set and constraint_set.intersection(resource.constraints):
                score += 0.5
            if capability_set.intersection(resource.tags):
                score += 0.25
            scores.append((score, resource))
        scores.sort(key=lambda item: (-item[0], item[1].name))
        return [resource for _, resource in scores]


__all__ = ["ToolResourceRecord", "ToolResourceStore"]
