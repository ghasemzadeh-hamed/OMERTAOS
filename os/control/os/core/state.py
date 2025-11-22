"""In-memory control plane state for the lightweight headless API."""
from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from os.control.os.agent_catalog.store import AgentRegistry
from os.control.os.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Provider:
    name: str
    kind: str
    base_url: str
    models: List[str]
    api_key: Optional[str] = None
    enabled: bool = True


@dataclass
class DataSource:
    name: str
    kind: str
    dsn: str
    enabled: bool = True


@dataclass
class Module:
    name: str
    version: str
    description: str
    enabled: bool = True


@dataclass
class RouterPolicySnapshot:
    revision: int
    checksum: str
    version: str
    document: Dict
    applied_at: float = field(default_factory=lambda: time.time())


@dataclass
class RouterPolicy:
    revision: int = 0
    document: Dict = field(default_factory=dict)
    checksum: str = ""
    version: str = "0.0.0"


@dataclass
class JobRecord:
    event_id: str
    event_type: str
    status: str
    detail: str
    timestamp: float = field(default_factory=lambda: time.time())


class ControlState:
    """Thread-safe state container used by API handlers and workers."""

    def __init__(self) -> None:
        self.providers: Dict[str, Provider] = {}
        self.datasources: Dict[str, DataSource] = {}
        self.modules: Dict[str, Module] = {}
        self.router_policy = RouterPolicy()
        self.router_policy_history: List[RouterPolicySnapshot] = []
        self.latencies: Dict[str, float] = {}
        self.idempotency: Dict[str, float] = {}
        self.jobs: List[JobRecord] = []
        self.agent_registry = AgentRegistry()
        self.event_queue: asyncio.Queue[Dict] = asyncio.Queue()
        self.lock = asyncio.Lock()

    async def add_provider(self, provider: Provider) -> None:
        async with self.lock:
            self.providers[provider.name] = provider
            logger.info("provider added", extra={"provider": provider.name})

    async def enable_provider(self, name: str, enabled: bool) -> None:
        async with self.lock:
            if name in self.providers:
                self.providers[name].enabled = enabled

    async def add_datasource(self, datasource: DataSource) -> None:
        async with self.lock:
            self.datasources[datasource.name] = datasource

    async def add_module(self, module: Module) -> None:
        async with self.lock:
            self.modules[module.name] = module

    async def set_router_policy(self, document: Dict) -> RouterPolicy:
        async with self.lock:
            if self.router_policy.revision > 0:
                snapshot = RouterPolicySnapshot(
                    revision=self.router_policy.revision,
                    checksum=self.router_policy.checksum,
                    version=self.router_policy.version,
                    document=copy.deepcopy(self.router_policy.document),
                )
                self.router_policy_history.append(snapshot)
                self.router_policy_history = self.router_policy_history[-20:]
            self.router_policy.revision += 1
            self.router_policy.document = copy.deepcopy(document)
            self.router_policy.version = str(document.get("version", "0.0.0"))
            serialized = json.dumps(self.router_policy.document, sort_keys=True).encode("utf-8")
            self.router_policy.checksum = hashlib.sha256(serialized).hexdigest()
            return self.router_policy

    async def rollback_router_policy(self, revision: Optional[int] = None) -> RouterPolicy:
        async with self.lock:
            if not self.router_policy_history:
                raise ValueError("no policy history available")
            if revision is None:
                target_snapshot = self.router_policy_history.pop()
            else:
                index = next(
                    (i for i, snapshot in enumerate(self.router_policy_history) if snapshot.revision == revision),
                    None,
                )
                if index is None:
                    raise ValueError("requested revision not found")
                target_snapshot = self.router_policy_history.pop(index)
            current_snapshot = RouterPolicySnapshot(
                revision=self.router_policy.revision,
                checksum=self.router_policy.checksum,
                version=self.router_policy.version,
                document=copy.deepcopy(self.router_policy.document),
            )
            self.router_policy_history.append(current_snapshot)
            self.router_policy_history = self.router_policy_history[-20:]
            self.router_policy.revision += 1
            self.router_policy.document = copy.deepcopy(target_snapshot.document)
            self.router_policy.version = target_snapshot.version
            self.router_policy.checksum = target_snapshot.checksum
            return self.router_policy

    def get_router_policy_history(self, limit: int = 10) -> List[RouterPolicySnapshot]:
        return self.router_policy_history[-limit:]

    async def record_latency(self, name: str, value_ms: float) -> None:
        async with self.lock:
            self.latencies[name] = value_ms

    async def enqueue_event(self, event: Dict) -> None:
        await self.event_queue.put(event)

    def check_idempotency(self, event_id: str, ttl_seconds: int = 300) -> bool:
        now = time.time()
        # purge expired entries
        expired = [key for key, expiry in self.idempotency.items() if expiry < now]
        for key in expired:
            del self.idempotency[key]
        if event_id in self.idempotency:
            return False
        self.idempotency[event_id] = now + ttl_seconds
        return True

    def record_job(self, record: JobRecord) -> None:
        self.jobs.append(record)
        self.jobs = self.jobs[-100:]

    def get_health_summary(self) -> Dict:
        return {
            "status": "ok",
            "details": {
                "providers": len(self.providers),
                "modules": len(self.modules),
                "datasources": len(self.datasources),
                "router_policy_rev": self.router_policy.revision,
                "router_policy_checksum": self.router_policy.checksum,
                "router_policy_version": self.router_policy.version,
                "queue_depth": self.event_queue.qsize(),
            },
            "latencies": self.latencies,
        }


STATE = ControlState()


def generate_event_id(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
