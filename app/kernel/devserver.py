"""Development kernel service exposing the v1 API surface described in the roadmap."""
from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


class AgentSpec(BaseModel):
    agent_id: str
    name: str
    version: str
    capabilities: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    manifest: Dict[str, Any] | None = None


class Heartbeat(BaseModel):
    agent_id: str
    status: str = "ready"
    metrics: Dict[str, Any] = Field(default_factory=dict)


class SyscallRequest(BaseModel):
    schema: str
    syscall: str
    agent_id: str
    context: Dict[str, Any] = Field(default_factory=dict)
    caps_required: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
    budget: Dict[str, Any] = Field(default_factory=dict)


class MemoryItem(BaseModel):
    type: str
    key: str
    value: Any
    meta: Dict[str, Any] = Field(default_factory=dict)


class MemoryQuery(BaseModel):
    type: str
    knn: Dict[str, Any] | None = None
    filter: Dict[str, Any] = Field(default_factory=dict)


class ScheduleTask(BaseModel):
    task_id: str
    intent: str
    priority: int = 5
    quota: Dict[str, Any] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)


class PolicySnapshot(BaseModel):
    metrics: Dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="AION Kernel Dev Server", version="0.1.0")


class AgentRegistry:
    agents: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, spec: AgentSpec, tenant: str) -> Dict[str, Any]:
        record = {
            "agent_id": spec.agent_id,
            "tenant": tenant,
            "name": spec.name,
            "version": spec.version,
            "capabilities": spec.capabilities,
            "limits": spec.limits,
            "manifest": spec.manifest or {},
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
            "status": "registered",
        }
        cls.agents[f"{tenant}:{spec.agent_id}"] = record
        return {"registered": True, "agent": record}

    @classmethod
    def heartbeat(cls, hb: Heartbeat, tenant: str) -> Dict[str, Any]:
        key = f"{tenant}:{hb.agent_id}"
        agent = cls.agents.get(key)
        if not agent:
            raise HTTPException(status_code=404, detail="agent not registered")
        agent["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        agent["status"] = hb.status
        agent.setdefault("metrics", {}).update(hb.metrics)
        return {"ok": True, "agent": agent}


class MemoryStore:
    store: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(lambda: defaultdict(dict))

    @classmethod
    def put(cls, item: MemoryItem, tenant: str) -> Dict[str, Any]:
        tier = item.type
        cls.store[tenant][tier][item.key] = {
            "value": item.value,
            "meta": item.meta,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        return {"stored": True}

    @classmethod
    def query(cls, q: MemoryQuery, tenant: str) -> Dict[str, Any]:
        tier = q.type
        entries = cls.store[tenant].get(tier, {})
        # naive filtering for development use
        filters = q.filter or {}
        results = []
        for key, payload in entries.items():
            if all(payload["meta"].get(k) == v for k, v in filters.items()):
                results.append({"key": key, **payload})
        return {"items": results, "count": len(results)}


class SchedulerQueue:
    queues: Dict[str, Deque[Dict[str, Any]]] = defaultdict(deque)

    @classmethod
    def submit(cls, task: ScheduleTask, tenant: str) -> Dict[str, Any]:
        queue = cls.queues[tenant]
        queue.append({"task": task.dict(), "ts": time.time()})
        return {"enqueued": True, "depth": len(queue)}


class PolicyBrain:
    versions: List[Dict[str, Any]] = []

    @classmethod
    def propose(cls, snapshot: PolicySnapshot) -> Dict[str, Any]:
        version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        bundle = {
            "version": version,
            "changes": {
                "thresholds": snapshot.metrics.get("thresholds", {}),
                "notes": "auto-generated from devserver",
            },
        }
        cls.versions.append(bundle)
        return bundle

    @classmethod
    def rollback(cls, version: str) -> Dict[str, Any]:
        for bundle in reversed(cls.versions):
            if bundle["version"] == version:
                return {"rolled_back": version, "bundle": bundle}
        raise HTTPException(status_code=404, detail="policy version not found")


@app.get("/healthz")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/agent/register")
def agent_register(spec: AgentSpec, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    return AgentRegistry.register(spec, tenant=x_tenant_id)


@app.post("/v1/agent/heartbeat")
def agent_heartbeat(hb: Heartbeat, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    return AgentRegistry.heartbeat(hb, tenant=x_tenant_id)


@app.post("/v1/syscall/{name}")
def syscall(name: str, payload: SyscallRequest, x_tenant_id: str = Header(...), x_sig_hmac: str = Header("dev")) -> Dict[str, Any]:
    key = f"{x_tenant_id}:{payload.agent_id}"
    if key not in AgentRegistry.agents:
        raise HTTPException(status_code=404, detail="agent not registered")

    audit_id = f"sc-{uuid.uuid4().hex[:10]}"
    return {
        "status": "ok",
        "result": {"echo": payload.params, "syscall": name},
        "usage": {"latency_ms": 5, "cost_usd": 0.0, "tokens_in": 0, "tokens_out": 0},
        "engine": {"kind": "dev", "name": "app.kernel.devserver"},
        "audit_id": audit_id,
        "signature": x_sig_hmac,
    }


@app.post("/v1/memory/put")
def memory_put(item: MemoryItem, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    return MemoryStore.put(item, tenant=x_tenant_id)


@app.post("/v1/memory/query")
def memory_query(q: MemoryQuery, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    return MemoryStore.query(q, tenant=x_tenant_id)


@app.post("/v1/schedule/submit")
def schedule_submit(task: ScheduleTask, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    return SchedulerQueue.submit(task, tenant=x_tenant_id)


@app.post("/v1/brain/propose-policy")
def propose_policy(snapshot: PolicySnapshot) -> Dict[str, Any]:
    return PolicyBrain.propose(snapshot)


@app.post("/v1/policy/rollback/{version}")
def rollback_policy(version: str) -> Dict[str, Any]:
    return PolicyBrain.rollback(version)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.kernel.devserver:app", host="0.0.0.0", port=8010, reload=False)
