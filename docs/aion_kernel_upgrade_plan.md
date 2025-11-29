AION-OS v2 - Kernel & AgentOS Upgrade (to surpass AIOS)

&#x647;&#x62f;&#x641;: &#x627;&#x631;&#x62a;&#x642;&#x627;&#x6cc; AION-OS &#x627;&#x632; "&#x67e;&#x644;&#x62a;&#x641;&#x631;&#x645; &#x686;&#x646;&#x62f;-Plane" &#x628;&#x647; "Agent-centric AI OS" &#x628;&#x627; Kernel &#x62f;&#x627;&#x62e;&#x644;&#x6cc;&#x60c; Syscall&#x60c; Context/Memory &#x633;&#x644;&#x633;&#x644;&#x647;&#x200c;&#x645;&#x631;&#x627;&#x62a;&#x628;&#x6cc;&#x60c; Scheduler &#x67e;&#x6cc;&#x634;&#x6af;&#x6cc;&#x631;&#x627;&#x646;&#x647;&#x60c; Sandbox &#x633;&#x637;&#x62d; &#x6a9;&#x631;&#x646;&#x644;&#x60c; SDK &#x631;&#x633;&#x645;&#x6cc;&#x60c; &#x648; &#x62d;&#x644;&#x642;&#x647;&#x654; &#x628;&#x647;&#x6cc;&#x646;&#x647;&#x200c;&#x633;&#x627;&#x632;&#x6cc; Policy-&#x62f;&#x631;&#x62d;&#x627;&#x644;&#x6cc;&#x200c;&#x6a9;&#x647; &#x645;&#x642;&#x6cc;&#x627;&#x633;&#x200c;&#x67e;&#x630;&#x6cc;&#x631;&#x6cc; &#x62a;&#x648;&#x632;&#x6cc;&#x639;&#x200c;&#x634;&#x62f;&#x647;&#x654; &#x641;&#x639;&#x644;&#x6cc; (Kafka/ClickHouse/...&#x200b;) &#x62d;&#x641;&#x638; &#x648; &#x62a;&#x642;&#x648;&#x6cc;&#x62a; &#x645;&#x6cc;&#x200c;&#x634;&#x648;&#x62f;.

&#x2e3b;

0. Roadmap (&#x6af;&#x627;&#x645;&#x200c;&#x647;&#x627;&#x6cc; &#x627;&#x62c;&#x631;&#x627;&#x6cc;&#x6cc;)
   *Core Kernel Service (/kernel): Manager + Syscalls + Memory + Sandbox + Feedback
   *Agent SDKs: Python (+TS) &#x628;&#x627; &#x6a9;&#x644;&#x627;&#x633;&#x200c;&#x647;&#x627;&#x6cc; Agent/Tool/Memory/Syscall/Event
   *Scheduler: &#x635;&#x641; Priority + preemption + quotas (SLA/Latency/Budget)
   *Hierarchical Memory: short/long/episodic + RAG + GC adaptive
   *Sandbox & Security: seccomp/cgroup/eBPF profiles + capability model
   *Policy Brain: &#x67e;&#x6cc;&#x634;&#x646;&#x647;&#x627;&#x62f; Policy &#x627;&#x632; Telemetry (vLLM/Ollama) + SafeKeeper rollback
   *Console Upgrade: &#x635;&#x641;&#x62d;&#x647;&#x654; Kernel (Agents/Process Table/Memory/Syscalls/Traces) + ChatOps
   *Observability: OTel spans+metrics&#x60c; &#x62f;&#x627;&#x634;&#x628;&#x648;&#x631;&#x62f; Grafana&#x60c; &#x644;&#x627;&#x6af; &#x633;&#x627;&#x62e;&#x62a;&#x627;&#x631;&#x6cc;&#x627;&#x641;&#x62a;&#x647;
   *CI/CD: &#x627;&#x645;&#x636;&#x627;&#x6cc; Cosign &#x628;&#x631;&#x627;&#x6cc; Agent/Tool&#x60c; &#x62a;&#x633;&#x62a; E2E&#x60c; &#x62a;&#x63a;&#x6cc;&#x6cc;&#x640;&#x631;&#x627;&#x62a; Compose &#x648; Migration DB
   *Docs & Samples: &#x646;&#x645;&#x648;&#x646;&#x647;&#x654; agent.yml&#x60c; tool.yml&#x60c; Syscall contract&#x60c; &#x62a;&#x633;&#x62a;&#x200c;&#x647;&#x627;&#x6cc; &#x646;&#x645;&#x648;&#x646;&#x647;

&#x2e3b;

1. &#x627;&#x641;&#x632;&#x648;&#x62f;&#x647;&#x200c;&#x647;&#x627;&#x6cc; &#x633;&#x627;&#x62e;&#x62a;&#x627;&#x631; &#x631;&#x6cc;&#x67e;&#x648;

/kernel/
&#x251c;&#x2500; aion_kernel/**init**.py
&#x251c;&#x2500; manager.py # Agent/Process table, lifecycle, heartbeats
&#x251c;&#x2500; syscalls.py # syscall routing + policy + audit
&#x251c;&#x2500; memory.py # short/long/episodic stores + adapters (Redis/Qdrant/MinIO)
&#x251c;&#x2500; sandbox/
&#x2502; &#x251c;&#x2500; seccomp_profile.json
&#x2502; &#x251c;&#x2500; cgroup_profiles.yaml
&#x2502; &#x2514;&#x2500; ebpf/
&#x251c;&#x2500; scheduler.py # priority queue + preemption + quotas
&#x251c;&#x2500; feedback.py # Policy Brain I/O + SafeKeeper
&#x2514;&#x2500; api.py # FastAPI app (mounted in control or standalone)

/sdk/
&#x251c;&#x2500; python/aion_sdk/
&#x2502; &#x251c;&#x2500; **init**.py
&#x2502; &#x251c;&#x2500; agent.py # Agent base, lifecycle hooks
&#x2502; &#x251c;&#x2500; memory.py # Memory client (short/long/episodic)
&#x2502; &#x251c;&#x2500; syscall.py # Call kernel syscalls w/ HMAC
&#x2502; &#x2514;&#x2500; events.py
&#x2514;&#x2500; ts/aion-sdk/
&#x251c;&#x2500; index.ts
&#x251c;&#x2500; agent.ts
&#x251c;&#x2500; memory.ts
&#x2514;&#x2500; syscall.ts

/config/
&#x251c;&#x2500; kernel.yaml # ttl/limits/capabilities defaults
&#x251c;&#x2500; memory.yaml # backends + TTL rules + eviction policy
&#x2514;&#x2500; scheduler.yaml # queues, weights, fairness, quotas

/policies/
&#x251c;&#x2500; agent.capabilities.yaml # global allow/deny
&#x2514;&#x2500; policy_versions/...

/console/app/(kernel)/_
/tests/e2e/kernel/_

&#x2e3b;

2. API &#x633;&#x637;&#x62d; Kernel (FastAPI)

# /kernel/api.py

from fastapi import FastAPI, Header, HTTPException
from .manager import AgentManager
from .syscalls import SyscallRouter
from .memory import MemoryService
from .scheduler import Scheduler
from .feedback import PolicyBrain

app = FastAPI(title="AION Kernel")

@app.post("/v1/agent/register")
def agent_register(spec: dict, x_tenant_id: str = Header(...)): # spec: {agent_id,name,version,capabilities,limits,manifest}
return AgentManager.register(spec, tenant=x_tenant_id)

@app.post("/v1/agent/heartbeat")
def agent_hb(hb: dict, x_tenant_id: str = Header(...)):
return AgentManager.heartbeat(hb, tenant=x_tenant_id)

@app.post("/v1/syscall/{name}")
def syscall(name: str, payload: dict, x_tenant_id: str = Header(...), x_sig_hmac: str = Header(...)): # verifies HMAC, policy, capability; logs audit
return SyscallRouter.dispatch(name, payload, tenant=x_tenant_id, sig=x_sig_hmac)

@app.post("/v1/memory/put")
def memory_put(item: dict, x_tenant_id: str = Header(...)): # item: {type:"short|long|episodic", key, value, meta}
return MemoryService.put(item, tenant=x_tenant_id)

@app.post("/v1/memory/query")
def memory_query(q: dict, x_tenant_id: str = Header(...)): # q: {type, knn:{vector|text,k}, filter:{}}
return MemoryService.query(q, tenant=x_tenant_id)

@app.post("/v1/schedule/submit")
def schedule_submit(task: dict, x_tenant_id: str = Header(...)): # task: {task_id,intent,priority,quota,params}
return Scheduler.submit(task, tenant=x_tenant_id)

@app.post("/v1/brain/propose-policy")
def propose_policy(snapshot: dict): # snapshot: aggregated metrics; returns new policy bundle
return PolicyBrain.propose(snapshot)

@app.post("/v1/policy/rollback/{version}")
def rollback(version: str):
return PolicyBrain.rollback(version)

Mounting: &#x6cc;&#x627; &#x627;&#x6cc;&#x646; &#x633;&#x631;&#x648;&#x6cc;&#x633; &#x631;&#x627; &#x62f;&#x631; control/ &#x628;&#x647;&#x200c;&#x635;&#x648;&#x631;&#x62a; &#x632;&#x6cc;&#x631;-&#x627;&#x67e; (FastAPI include_router) &#x633;&#x648;&#x627;&#x631; &#x6a9;&#x646;&#x6cc;&#x645;&#x60c; &#x6cc;&#x627; &#x628;&#x647; &#x639;&#x646;&#x648;&#x627;&#x646; &#x633;&#x631;&#x648;&#x6cc;&#x633; &#x62c;&#x62f;&#x627; &#x628;&#x627; Auth &#x62f;&#x627;&#x62e;&#x644;&#x6cc; (OIDC/JWT + HMAC) &#x628;&#x627;&#x644;&#x627; &#x628;&#x6cc;&#x627;&#x648;&#x631;&#x6cc;&#x645;.

&#x2e3b;

3. &#x642;&#x631;&#x627;&#x631;&#x62f;&#x627;&#x62f; Syscall (JSON)

&#x62f;&#x631;&#x62e;&#x648;&#x627;&#x633;&#x62a;

{
"schema": "aion.syscall.v1",
"syscall": "tool.invoke", // &#x646;&#x645;&#x648;&#x646;&#x647;: tool.invoke, model.generate, fs.read, net.fetch
"agent_id": "agent://tenantA/researcher-1",
"context": { "task_id": "t-123", "trace_id": "..." },
"caps_required": ["network","gpu"], // cross-check &#x628;&#x627; capabilities agent/tenant
"params": { "tool": "web_search", "query": "..." },
"budget": { "usd_max": 0.05, "latency_ms": 3000 }
}

&#x67e;&#x627;&#x633;&#x62e;

{
"status": "ok",
"result": { "items": [ /* ... */ ] },
"usage": { "latency_ms": 412, "cost_usd": 0.002, "tokens_in": 0, "tokens_out": 0 },
"engine": { "kind": "module", "name": "tooling/web_search@1.2.0" },
"audit_id": "sc-9f2a..."
}

&#x2e3b;

4. Manifest&#x647;&#x627;

agent.yml

apiVersion: aion.os/v1
kind: Agent
metadata:
name: "researcher"
version: "1.0.0"
spec:
entry: "python -m my_agent.start"
priority: 5
timeout_ms: 120000
memory:
short_ttl_s: 3600
long_ttl_s: 1209600
episodic_ttl_s: 259200
capabilities:
filesystem: false
network: true
gpu: true
subprocess: false
syscalls: - tool.invoke - model.generate - memory.\* # put/query
resources:
cpu: "1000m"
mem: "1Gi"
gpu: "optional"
policy_overrides:
sla:
p95_ms: 2500
budget:
usd_max: 0.10
privacy:
allow_cloud: false

tool.yml

apiVersion: aion.os/v1
kind: Tool
metadata: { name: "web_search", version: "1.2.0" }
spec:
entry: "wasm:tools/web_search.wasm" # &#x6cc;&#x627; "rust:bin/web_search"
io:
input: { schema: "query:string" }
output: { schema: "items:list" }
capabilities_required: ["network"]
security:
seccomp_profile: "default-restrictive"
cgroup: "tool-low"
signatures:
cosign: "sigstore://..."

&#x2e3b;

5. Scheduler (Preemptive + Quotas)
   *Queues: high, normal, low &#x628;&#x627; &#x648;&#x632;&#x646;&#x200c;&#x647;&#x627; &#x62f;&#x631; config/scheduler.yaml
   *Preemption: &#x627;&#x6af;&#x631; job &#x628;&#x627; priority &#x628;&#x627;&#x644;&#x627;&#x62a;&#x631; &#x628;&#x631;&#x633;&#x62f;&#x60c; job &#x62c;&#x627;&#x631;&#x6cc; checkpoint &#x645;&#x6cc;&#x200c;&#x634;&#x648;&#x62f; (snapshot &#x62f;&#x631; Redis/MinIO)
   *Quotas: &#x628;&#x631; &#x627;&#x633;&#x627;&#x633; tenant/agent (max_concurrency, token_rate, usd_per_hour)
   *Backpressure: &#x628;&#x627; Redis Streams &#x6cc;&#x627; PriorityQueue &#x62f;&#x631; &#x62d;&#x627;&#x641;&#x638;&#x647; + persistent journal

&#x646;&#x645;&#x648;&#x646;&#x647;&#x200c;&#x6cc; &#x627;&#x633;&#x6a9;&#x644;&#x62a;:

# /kernel/scheduler.py

import time, heapq
class Scheduler:
pq = [] # (priority, ts, task)
@classmethod
def submit(cls, task, tenant):
item = (task["priority"], time.time(), task)
heapq.heappush(cls.pq, item)
return {"enqueued": True, "size": len(cls.pq)}
@classmethod
def next(cls):
if not cls.pq: return None
return heapq.heappop(cls.pq)[2]

&#x62f;&#x631; &#x639;&#x645;&#x644;: &#x628;&#x647; Redis Streams + worker&#x647;&#x627;&#x6cc; async &#x62a;&#x628;&#x62f;&#x6cc;&#x644; &#x645;&#x6cc;&#x200c;&#x634;&#x648;&#x62f;&#x61b; preemption &#x628;&#x627; checkpoint &#x62f;&#x631; /kernel/memory.

&#x2e3b;

6. Memory &#x633;&#x644;&#x633;&#x644;&#x647;&#x200c;&#x645;&#x631;&#x627;&#x62a;&#x628;&#x6cc; + RAG

&#x67e;&#x6cc;&#x6a9;&#x631;&#x628;&#x646;&#x62f;&#x6cc;

# /config/memory.yaml

backends:
short:
driver: redis
ttl_s: 3600
long:
driver: qdrant
ttl_s: 1209600
collection: "aion_long_memory"
episodic:
driver: minio
ttl_s: 259200
bucket: "aion-episodic"
gc:
strategy: "adaptive"
watermarks:
high: 0.85
low: 0.60

&#x6a9;&#x644;&#x6cc;&#x62f;&#x647;&#x627;/&#x6a9;&#x627;&#x644;&#x6a9;&#x634;&#x646;&#x200c;&#x647;&#x627;
*Redis: mem:{tenant}:{agent}:{task}:{key}
*Qdrant: collection aion_long_memory (payload: tenant, agent, tags, ts)
\*MinIO: episodic/{tenant}/{agent}/{day}/{uuid}.jsonl

RAG API

POST /v1/memory/query
{ "type":"long", "knn": { "text":"...", "k":8 }, "filter":{"tenant":"...","agent":"..."} }

&#x2e3b;

7. Sandbox & Security
   *seccomp: kernel/sandbox/seccomp_profile.json (deny-by-default&#x60c; allow minimal syscalls)
   *cgroup: kernel/sandbox/cgroup_profiles.yaml (cpu/mem/gpu quotas)
   *eBPF probes: latency/IO anomalies &#x2192; &#x627;&#x631;&#x633;&#x627;&#x644; &#x628;&#x647; Prometheus
   *HMAC &#x628;&#x631;&#x627;&#x6cc; Syscall: Header X-SIG-HMAC (sha256) &#x628;&#x627; secret tenant
   \*Cosign: &#x627;&#x645;&#x636;&#x627;&#x6cc; agent.yml &#x648; tool.yml + SBOM &#x62f;&#x631; CI

&#x2e3b;

8. Policy Brain + SafeKeeper
   *Brain: &#x633;&#x631;&#x648;&#x6cc;&#x633; &#x6a9;&#x648;&#x686;&#x6a9;&#x6cc; &#x6a9;&#x647; &#x627;&#x632; &#x622;&#x645;&#x627;&#x631; Router/Scheduler/Memory&#x60c; &#x67e;&#x6cc;&#x634;&#x646;&#x647;&#x627;&#x62f; policies/ &#x62c;&#x62f;&#x6cc;&#x62f; &#x645;&#x6cc;&#x200c;&#x633;&#x627;&#x632;&#x62f; (LLM &#x645;&#x62d;&#x644;&#x6cc;: Ollama/vLLM)
   *SafeKeeper: health gates (p95 latency, error_rate, cost/hour) &#x2192; &#x62f;&#x631; &#x635;&#x648;&#x631;&#x62a; &#x627;&#x646;&#x62d;&#x631;&#x627;&#x641; rollback &#x628;&#x647; policy_versions/{ver}

&#x646;&#x645;&#x648;&#x646;&#x647; &#x627;&#x6cc;&#x646;&#x62a;&#x631;&#x641;&#x6cc;&#x633;:

# /kernel/feedback.py

class PolicyBrain:
@staticmethod
def propose(snapshot: dict) -> dict: # run LLM prompt &#x2192; new bundle
return {"version": "2025-11-03-01", "changes": {...}}

    @staticmethod
    def rollback(version: str) -> dict:
        # atomically switch symlink &#x2192; policies/current -> policies/policy_versions/{version}
        return {"rolled_back": version}

&#x2e3b;

9. SDK &#x646;&#x645;&#x648;&#x646;&#x647; (Python)

# /sdk/python/aion_sdk/agent.py

import os, requests, hmac, hashlib, json

class Agent:
def **init**(self, agent_id, kernel_url, secret, tenant):
self.agent_id = agent_id
self.kernel_url = kernel_url
self.secret = secret.encode()
self.tenant = tenant

    def _hmac(self, body: bytes):
        return hmac.new(self.secret, body, hashlib.sha256).hexdigest()

    def syscall(self, name: str, payload: dict):
        body = json.dumps({
            "schema": "aion.syscall.v1",
            "syscall": name,
            "agent_id": self.agent_id,
            "context": {},
            "caps_required": [],
            "params": payload
        }).encode()
        sig = self._hmac(body)
        r = requests.post(f"{self.kernel_url}/v1/syscall/{name}",
                          data=body,
                          headers={"Content-Type":"application/json",
                                   "X-Tenant-Id": self.tenant,
                                   "X-Sig-HMAC": sig})
        r.raise_for_status()
        return r.json()

&#x2e3b;

10. &#x627;&#x631;&#x62a;&#x642;&#x627;&#x6cc; Console (Next.js)
    *&#x645;&#x633;&#x6cc;&#x631; &#x62c;&#x62f;&#x6cc;&#x62f;: /kernel &#x628;&#x627; &#x62a;&#x628;&#x200c;&#x647;&#x627;&#x6cc;:
    *Agents (process table: agent_id, state, cpu, mem, gpu, queue, age)
    *Memory (short/long/episodic usage + GC)
    *Syscalls (live stream &#x628;&#x627; WebSocket + filters)
    *Scheduler (queue depth, p95, fairness)
    *Policy (current/versions, diff, propose, rollback)
    \*ChatOps Terminal: /kernel/terminal &#x628;&#x627; slash-commands:
    /agent status, /syscall trace {agent}, /policy diff, /memory top

Backend WS: GET /v1/events/stream?topics=kernel.syscalls,kernel.scheduler,kernel.gc

&#x2e3b;

11. Observability

Metrics (Prometheus):
*aion_kernel_scheduler_queue_depth{queue}
*aion_kernel_syscall_latency_ms{syscall}
*aion_kernel_preemption_count
*aion_memory_gc_events_total{kind}
*aion_policy_rollbacks_total
*aion_agent_heartbeats{tenant,agent}

Traces (OTel):
\*span names: kernel.syscall, kernel.schedule, kernel.memory.query, kernel.policy.propose

&#x2e3b;

12. CI/CD & &#x627;&#x645;&#x646;&#x6cc;&#x62a; Supply-Chain
    *GitHub Actions:
    *Build & Test: kernel + sdk + console pages
    *Security: Trivy + SBOM (Syft)
    *Cosign: sign agent/tool artifacts + verify in deploy job
    \*E2E: docker-compose core+kernel&#x60c; &#x633;&#x646;&#x627;&#x631;&#x6cc;&#x648; Route&#x2192;Syscall&#x2192;Memory&#x2192;Analytics

&#x2e3b;

13. Compose &#x62a;&#x63a;&#x6cc;&#x6cc;&#x631;&#x627;&#x62a; (&#x646;&#x645;&#x648;&#x646;&#x647;&#x654; &#x633;&#x631;&#x648;&#x6cc;&#x633; Kernel)

# docker-compose.kernel.yml

services:
aion-kernel:
build: ./kernel
environment: - AION_KERNEL_PORT=8010 - REDIS_URL=redis://redis:6379/3 - QDRANT_URL=http://qdrant:6333 - MINIO_URL=http://minio:9000 - OLLAMA_URL=http://llm:11434 - POLICY_DIR=/policies
ports: - "8010:8010"
depends_on: [redis, qdrant, minio]

&#x2e3b;

14. &#x62c;&#x62f;&#x648;&#x644; Services x Ports x Env (&#x62e;&#x644;&#x627;&#x635;&#x647;)

ServicePortKey ENV
Console3001NEXT_PUBLIC_GATEWAY_URL, NEXT_PUBLIC_KERNEL_URL
Gateway3000AION_GATEWAY*_
Control8001AION*CONTROL*_, DB/Redis/Kafka/Qdrant/MinIO
Kernel8010REDIS*URL, QDRANT_URL, MINIO_URL, POLICY_DIR
vLLM (opt)8008MODEL*\*
Kafka/CH/etc....KAFKA_BROKERS, CLICKHOUSE_URL

&#x2e3b;

15. &#x62a;&#x633;&#x62a;&#x200c;&#x647;&#x627;&#x6cc; &#x67e;&#x630;&#x6cc;&#x631;&#x634; (Acceptance)
    1.Syscall round-trip: Agent&#x2192;/v1/syscall/tool.invoke&#x2192;Tool&#x2192;Result (&#x2264; p95 2.5s)
    2.Scheduler preemption: &#x627;&#x631;&#x633;&#x627;&#x644; job high-priority &#x648; &#x642;&#x637;&#x639; &#x645;&#x646;&#x635;&#x641;&#x627;&#x646;&#x647;&#x654; job &#x62c;&#x627;&#x631;&#x6cc; &#x628;&#x627; checkpoint
    3.Memory RAG: put&#x2192;query (KNN)&#x2192;&#x646;&#x62a;&#x6cc;&#x62c;&#x647; &#x628;&#x627; filter tenant/agent &#x635;&#x62d;&#x6cc;&#x62d;
    4.Capability enforcement: Agent &#x628;&#x62f;&#x648;&#x646; network &#x646;&#x62a;&#x648;&#x627;&#x646;&#x62f; tool:web_search &#x631;&#x627; invoke &#x6a9;&#x646;&#x62f;
    5.Policy Brain propose + rollback: &#x62a;&#x648;&#x644;&#x6cc;&#x62f; &#x646;&#x633;&#x62e;&#x647;&#x654; &#x62c;&#x62f;&#x6cc;&#x62f; + rollback &#x62e;&#x648;&#x62f;&#x6a9;&#x627;&#x631; &#x62f;&#x631; &#x627;&#x646;&#x62d;&#x631;&#x627;&#x641; KPI
    6.Console Kernel pages: &#x646;&#x645;&#x627;&#x6cc;&#x634; &#x632;&#x646;&#x62f;&#x647;&#x654; queue depth, syscalls, memory usage, traces
    7.OTel/Grafana: &#x645;&#x62a;&#x631;&#x6cc;&#x6a9;&#x200c;&#x647;&#x627; &#x648; &#x646;&#x645;&#x648;&#x62f;&#x627;&#x631;&#x647;&#x627; &#x628;&#x627;&#x644;&#x627; &#x628;&#x6cc;&#x627;&#x6cc;&#x62f;&#x61b; &#x644;&#x627;&#x6af; &#x633;&#x627;&#x62e;&#x62a;&#x627;&#x631;&#x6cc;&#x627;&#x641;&#x62a;&#x647;

&#x2e3b;

16. &#x646;&#x645;&#x648;&#x62f;&#x627;&#x631; Sequence (Mermaid)

sequenceDiagram
participant UI as Console/ChatOps
participant GW as Gateway
participant CT as Control
participant KN as Kernel
participant TL as Tool/Module
participant DB as Redis/Qdrant/MinIO

UI->>GW: Create Task (intent, SLA)
GW->>CT: /tasks/submit
CT->>KN: /v1/schedule/submit
KN->>KN: enqueue + possibly preempt
UI->>KN: /v1/syscall/tool.invoke (via Agent/SDK)
KN->>TL: sandboxed invoke (seccomp/cgroup)
TL->>DB: memory.read / write (short/long/episodic)
TL-->>KN: result + usage
KN-->>UI: syscall result (stream)
CT-->>Analytics: Kafka events -> ClickHouse -> Superset

&#x2e3b;

17. &#x646;&#x645;&#x648;&#x646;&#x647;&#x654; &#x62d;&#x62f;&#x627;&#x642;&#x644;&#x6cc; Agent (Python)

# examples/agents/researcher/main.py

from aion_sdk.agent import Agent
agent = Agent(agent_id="agent://tenantA/researcher-1",
kernel_url="http://localhost:8010",
secret="TENANT_A_SECRET",
tenant="tenantA")

res = agent.syscall("tool.invoke", {"tool":"web_search","query":"AION-OS Kernel"})
print(res)

&#x2e3b;

&#x646;&#x62a;&#x6cc;&#x62c;&#x647;

&#x628;&#x627; &#x627;&#x6cc;&#x646; &#x627;&#x631;&#x62a;&#x642;&#x627;:
_Kernel &#x62d;&#x642;&#x6cc;&#x642;&#x6cc; + syscall + context/memory &#x62f;&#x631;&#x648;&#x646;&#x200c;&#x633;&#x627;&#x632;&#x645;&#x627;&#x646;&#x6cc; (&#x645;&#x627;&#x646;&#x646;&#x62f; AIOS) &#x631;&#x627; &#x62f;&#x627;&#x631;&#x6cc;&#x645;&#x60c;
_&#x627;&#x645;&#x627; &#x645;&#x642;&#x6cc;&#x627;&#x633; &#x62a;&#x648;&#x632;&#x6cc;&#x639;&#x200c;&#x634;&#x62f;&#x647;&#x60c; &#x633;&#x6cc;&#x627;&#x633;&#x62a;&#x200c;&#x645;&#x62d;&#x648;&#x631;&#x6cc;/&#x627;&#x645;&#x646;&#x6cc;&#x62a; &#x633;&#x627;&#x632;&#x645;&#x627;&#x646;&#x6cc;&#x60c; &#x648; &#x644;&#x627;&#x6cc;&#x647;&#x654; &#x62f;&#x627;&#x62f;&#x647;&#x654; &#x628;&#x632;&#x631;&#x6af; AION-OS &#x631;&#x627; &#x647;&#x645; &#x62d;&#x641;&#x638; &#x648; &#x62a;&#x642;&#x648;&#x6cc;&#x62a; &#x645;&#x6cc;&#x200c;&#x6a9;&#x646;&#x6cc;&#x645;-&#x628;&#x646;&#x627;&#x628;&#x631;&#x627;&#x6cc;&#x646; &#x646;&#x647;&#x200c;&#x62a;&#x646;&#x647;&#x627; &#x647;&#x645;&#x200c;&#x62a;&#x631;&#x627;&#x632; AIOS&#x60c; &#x628;&#x644;&#x6a9;&#x647; &#x628;&#x631;&#x62a;&#x631; &#x627;&#x632; &#x622;&#x646; &#x628;&#x631;&#x627;&#x6cc; &#x633;&#x646;&#x627;&#x631;&#x6cc;&#x648;&#x647;&#x627;&#x6cc; &#x62a;&#x648;&#x644;&#x6cc;&#x62f;&#x6cc; &#x648; Enterprise &#x62e;&#x648;&#x627;&#x647;&#x6cc;&#x645; &#x628;&#x648;&#x62f;.

&#x2e3b;

PR &#x645;&#x62d;&#x62a;&#x648;&#x6cc;&#x627;&#x62a; &#x67e;&#x6cc;&#x634;&#x646;&#x647;&#x627;&#x62f;&#x6cc;
*kernel/ (&#x6a9;&#x62f; &#x628;&#x627;&#x644;&#x627; + &#x627;&#x633;&#x6a9;&#x644;&#x62a;&#x200c;&#x647;&#x627;)
*sdk/python/aion_sdk/ + sdk/ts/aion-sdk/
*config/kernel.yaml, config/memory.yaml, config/scheduler.yaml
*policies/agent.capabilities.yaml + policies/policy_versions/ (&#x646;&#x645;&#x648;&#x646;&#x647;)
*docker-compose.kernel.yml
*console/app/(kernel)/{agents,syscalls,memory,policy,terminal}/page.tsx (&#x627;&#x633;&#x6a9;&#x644;&#x62a;)
*tests/e2e/kernel/{syscall_roundtrip.test.py, scheduler_preempt.test.py, memory_rag.test.py}
*docs/aion_kernel_upgrade_plan.md (&#x647;&#x645;&#x6cc;&#x646; &#x641;&#x627;&#x6cc;&#x644;)
