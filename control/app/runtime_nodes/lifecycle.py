from __future__ import annotations

import asyncio
import json
import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Awaitable, Callable

import grpc
from sqlalchemy.orm import Session

from control.app.network.models import SessionLocal, init_db
from control.scheduling import (
    NodeState,
    RuntimeNodeHeartbeat,
    RuntimeNodeRegistration,
    RuntimeScheduler,
)
from control.scheduling.models import RuntimeNode
from shared.generated.python.runtime import runtime_pb2, runtime_pb2_grpc

logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]
RuntimeProbe = Callable[[str, float], Awaitable[bool]]


def _csv(value: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item.strip() for item in value.split(",") if item.strip()))


def _positive_int(env: Mapping[str, str], name: str, default: int) -> int:
    try:
        value = int(env.get(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _positive_float(env: Mapping[str, str], name: str, default: float) -> float:
    try:
        value = float(env.get(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


@dataclass(frozen=True, slots=True)
class RuntimeLifecycleConfig:
    enabled: bool
    node_id: str
    endpoint: str
    capabilities: tuple[str, ...]
    tenant_ids: tuple[str, ...]
    total_cpu_millis: int
    total_memory_mb: int
    heartbeat_interval_seconds: float
    probe_timeout_seconds: float

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "RuntimeLifecycleConfig":
        values = os.environ if env is None else env
        enabled_value = values.get("AION_RUNTIME_AUTO_REGISTER", "false").strip().lower()
        if enabled_value not in {"true", "false", "1", "0"}:
            raise ValueError("AION_RUNTIME_AUTO_REGISTER must be true or false")

        node_id = values.get("AION_RUNTIME_NODE_ID", "runtime-quickstart-1").strip()
        endpoint = values.get("AION_RUNTIME_ENDPOINT", "runtime:50051").strip()
        capabilities = _csv(
            values.get("AION_RUNTIME_CAPABILITIES", "terminal.execute")
        )
        interval = _positive_float(
            values, "AION_RUNTIME_HEARTBEAT_INTERVAL_SECONDS", 10.0
        )
        timeout = _positive_float(values, "AION_RUNTIME_PROBE_TIMEOUT_SECONDS", 3.0)

        if not node_id or len(node_id) > 120:
            raise ValueError("AION_RUNTIME_NODE_ID must contain 1 to 120 characters")
        if not endpoint or len(endpoint) > 255:
            raise ValueError("AION_RUNTIME_ENDPOINT must contain 1 to 255 characters")
        if not capabilities:
            raise ValueError("AION_RUNTIME_CAPABILITIES must not be empty")
        if interval > 20:
            raise ValueError(
                "AION_RUNTIME_HEARTBEAT_INTERVAL_SECONDS must not exceed 20"
            )
        if timeout > interval:
            raise ValueError(
                "AION_RUNTIME_PROBE_TIMEOUT_SECONDS must not exceed the heartbeat interval"
            )

        return cls(
            enabled=enabled_value in {"true", "1"},
            node_id=node_id,
            endpoint=endpoint,
            capabilities=capabilities,
            tenant_ids=_csv(values.get("AION_RUNTIME_TENANT_IDS", "")),
            total_cpu_millis=_positive_int(
                values, "AION_RUNTIME_TOTAL_CPU_MILLIS", 1000
            ),
            total_memory_mb=_positive_int(
                values, "AION_RUNTIME_TOTAL_MEMORY_MB", 512
            ),
            heartbeat_interval_seconds=interval,
            probe_timeout_seconds=timeout,
        )


async def probe_runtime(endpoint: str, timeout_seconds: float) -> bool:
    channel = grpc.aio.insecure_channel(endpoint)
    try:
        stub = runtime_pb2_grpc.RuntimeServiceStub(channel)
        response = await stub.QueryMetrics(
            runtime_pb2.MetricsRequest(tenant_id="system"),
            timeout=timeout_seconds,
        )
        if not response.ok:
            return False
        payload = json.loads(response.json)
        return payload.get("status") == "ready"
    except (grpc.RpcError, json.JSONDecodeError, TypeError):
        return False
    finally:
        await channel.close()


class RuntimeNodeLifecycle:
    def __init__(
        self,
        config: RuntimeLifecycleConfig,
        *,
        scheduler: RuntimeScheduler | None = None,
        session_factory: SessionFactory = SessionLocal,
        probe: RuntimeProbe = probe_runtime,
        schema_initializer: Callable[[], None] = init_db,
    ) -> None:
        self.config = config
        self.scheduler = scheduler or RuntimeScheduler()
        self.session_factory = session_factory
        self.probe = probe
        self.schema_initializer = schema_initializer
        self._reachable: bool | None = None

    async def sync_once(self) -> bool:
        reachable = bool(
            await self.probe(
                self.config.endpoint,
                self.config.probe_timeout_seconds,
            )
        )
        if not reachable:
            self._log_reachability(False)
            return False

        self.schema_initializer()
        with self.session_factory() as db:
            node = db.get(RuntimeNode, self.config.node_id)
            if node is None:
                self.scheduler.register_node(
                    db,
                    RuntimeNodeRegistration(
                        node_id=self.config.node_id,
                        endpoint=self.config.endpoint,
                        capabilities=self.config.capabilities,
                        tenant_ids=self.config.tenant_ids,
                        total_cpu_millis=self.config.total_cpu_millis,
                        total_memory_mb=self.config.total_memory_mb,
                        available_cpu_millis=self.config.total_cpu_millis,
                        available_memory_mb=self.config.total_memory_mb,
                        software_version="quickstart",
                        contract_version="runtime.v1",
                        trust_zone="local-quickstart",
                        labels={"managed_by": "control-runtime-lifecycle"},
                    ),
                    actor="runtime-lifecycle",
                )
            elif node.endpoint != self.config.endpoint:
                logger.error(
                    "Runtime lifecycle endpoint differs from the persisted node; refusing heartbeat"
                )
                return False

            self.scheduler.record_heartbeat(
                db,
                self.config.node_id,
                RuntimeNodeHeartbeat(
                    available_cpu_millis=self.config.total_cpu_millis,
                    available_memory_mb=self.config.total_memory_mb,
                    active_leases=0,
                    state=NodeState.healthy,
                    capabilities=self.config.capabilities,
                ),
                actor="runtime-lifecycle",
            )

        self._log_reachability(True)
        return True

    async def run(self) -> None:
        while True:
            try:
                await self.sync_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Runtime lifecycle synchronization failed")
            await asyncio.sleep(self.config.heartbeat_interval_seconds)

    def _log_reachability(self, reachable: bool) -> None:
        if self._reachable is reachable:
            return
        self._reachable = reachable
        log = logger.info if reachable else logger.warning
        log(
            "Runtime lifecycle reachability changed: node=%s reachable=%s",
            self.config.node_id,
            reachable,
        )
