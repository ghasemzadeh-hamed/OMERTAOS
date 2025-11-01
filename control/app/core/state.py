"""In-memory control plane state for the lightweight headless API."""
from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .logger import get_logger

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
class RouterPolicy:
    revision: int = 0
    document: Dict = field(default_factory=dict)


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
        self.latencies: Dict[str, float] = {}
        self.idempotency: Dict[str, float] = {}
        self.jobs: List[JobRecord] = []
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
            self.router_policy.revision += 1
            self.router_policy.document = document
            return self.router_policy

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
                "queue_depth": self.event_queue.qsize(),
            },
            "latencies": self.latencies,
        }


STATE = ControlState()


def generate_event_id(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
