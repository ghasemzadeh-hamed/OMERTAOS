AION-OS v2 — Kernel & AgentOS Upgrade (to surpass AIOS)

هدف: ارتقای AION-OS از “پلتفرم چند-Plane” به “Agent-centric AI OS” با Kernel داخلی، Syscall، Context/Memory سلسله‌مراتبی، Scheduler پیشگیرانه، Sandbox سطح کرنل، SDK رسمی، و حلقهٔ بهینه‌سازی Policy—درحالی‌که مقیاس‌پذیری توزیع‌شدهٔ فعلی (Kafka/ClickHouse/…​) حفظ و تقویت می‌شود.

⸻

0) Roadmap (گام‌های اجرایی)
•Core Kernel Service (/kernel): Manager + Syscalls + Memory + Sandbox + Feedback
•Agent SDKs: Python (+TS) با کلاس‌های Agent/Tool/Memory/Syscall/Event
•Scheduler: صف Priority + preemption + quotas (SLA/Latency/Budget)
•Hierarchical Memory: short/long/episodic + RAG + GC adaptive
•Sandbox & Security: seccomp/cgroup/eBPF profiles + capability model
•Policy Brain: پیشنهاد Policy از Telemetry (vLLM/Ollama) + SafeKeeper rollback
•Console Upgrade: صفحهٔ Kernel (Agents/Process Table/Memory/Syscalls/Traces) + ChatOps
•Observability: OTel spans+metrics، داشبورد Grafana، لاگ ساختاریافته
•CI/CD: امضای Cosign برای Agent/Tool، تست E2E، تغییـرات Compose و Migration DB
•Docs & Samples: نمونهٔ agent.yml، tool.yml، Syscall contract، تست‌های نمونه

⸻

1) افزوده‌های ساختار ریپو

/kernel/
  ├─ aion_kernel/__init__.py
  ├─ manager.py              # Agent/Process table, lifecycle, heartbeats
  ├─ syscalls.py             # syscall routing + policy + audit
  ├─ memory.py               # short/long/episodic stores + adapters (Redis/Qdrant/MinIO)
  ├─ sandbox/
  │   ├─ seccomp_profile.json
  │   ├─ cgroup_profiles.yaml
  │   └─ ebpf/
  ├─ scheduler.py            # priority queue + preemption + quotas
  ├─ feedback.py             # Policy Brain I/O + SafeKeeper
  └─ api.py                  # FastAPI app (mounted in control or standalone)
  
/sdk/
  ├─ python/aion_sdk/
  │   ├─ __init__.py
  │   ├─ agent.py            # Agent base, lifecycle hooks
  │   ├─ memory.py           # Memory client (short/long/episodic)
  │   ├─ syscall.py          # Call kernel syscalls w/ HMAC
  │   └─ events.py
  └─ ts/aion-sdk/
      ├─ index.ts
      ├─ agent.ts
      ├─ memory.ts
      └─ syscall.ts

/config/
  ├─ kernel.yaml             # ttl/limits/capabilities defaults
  ├─ memory.yaml             # backends + TTL rules + eviction policy
  └─ scheduler.yaml          # queues, weights, fairness, quotas

/policies/
  ├─ agent.capabilities.yaml # global allow/deny
  └─ policy_versions/...

/console/app/(kernel)/*
/tests/e2e/kernel/*


⸻

2) API سطح Kernel (FastAPI)

# /kernel/api.py
from fastapi import FastAPI, Header, HTTPException
from .manager import AgentManager
from .syscalls import SyscallRouter
from .memory import MemoryService
from .scheduler import Scheduler
from .feedback import PolicyBrain

app = FastAPI(title="AION Kernel")

@app.post("/v1/agent/register")
def agent_register(spec: dict, x_tenant_id: str = Header(...)):
    # spec: {agent_id,name,version,capabilities,limits,manifest}
    return AgentManager.register(spec, tenant=x_tenant_id)

@app.post("/v1/agent/heartbeat")
def agent_hb(hb: dict, x_tenant_id: str = Header(...)):
    return AgentManager.heartbeat(hb, tenant=x_tenant_id)

@app.post("/v1/syscall/{name}")
def syscall(name: str, payload: dict, x_tenant_id: str = Header(...), x_sig_hmac: str = Header(...)):
    # verifies HMAC, policy, capability; logs audit
    return SyscallRouter.dispatch(name, payload, tenant=x_tenant_id, sig=x_sig_hmac)

@app.post("/v1/memory/put")
def memory_put(item: dict, x_tenant_id: str = Header(...)):
    # item: {type:"short|long|episodic", key, value, meta}
    return MemoryService.put(item, tenant=x_tenant_id)

@app.post("/v1/memory/query")
def memory_query(q: dict, x_tenant_id: str = Header(...)):
    # q: {type, knn:{vector|text,k}, filter:{}}
    return MemoryService.query(q, tenant=x_tenant_id)

@app.post("/v1/schedule/submit")
def schedule_submit(task: dict, x_tenant_id: str = Header(...)):
    # task: {task_id,intent,priority,quota,params}
    return Scheduler.submit(task, tenant=x_tenant_id)

@app.post("/v1/brain/propose-policy")
def propose_policy(snapshot: dict):
    # snapshot: aggregated metrics; returns new policy bundle
    return PolicyBrain.propose(snapshot)

@app.post("/v1/policy/rollback/{version}")
def rollback(version: str):
    return PolicyBrain.rollback(version)

Mounting: یا این سرویس را در control/ به‌صورت زیر-اپ (FastAPI include_router) سوار کنیم، یا به عنوان سرویس جدا با Auth داخلی (OIDC/JWT + HMAC) بالا بیاوریم.

⸻

3) قرارداد Syscall (JSON)

درخواست

{
  "schema": "aion.syscall.v1",
  "syscall": "tool.invoke",                     // نمونه: tool.invoke, model.generate, fs.read, net.fetch
  "agent_id": "agent://tenantA/researcher-1",
  "context": { "task_id": "t-123", "trace_id": "..." },
  "caps_required": ["network","gpu"],           // cross-check با capabilities agent/tenant
  "params": { "tool": "web_search", "query": "..." },
  "budget": { "usd_max": 0.05, "latency_ms": 3000 }
}

پاسخ

{
  "status": "ok",
  "result": { "items": [ /* ... */ ] },
  "usage": { "latency_ms": 412, "cost_usd": 0.002, "tokens_in": 0, "tokens_out": 0 },
  "engine": { "kind": "module", "name": "tooling/web_search@1.2.0" },
  "audit_id": "sc-9f2a..."
}


⸻

4) Manifestها

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
  syscalls:
    - tool.invoke
    - model.generate
    - memory.*           # put/query
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
  entry: "wasm:tools/web_search.wasm"   # یا "rust:bin/web_search"
  io:
    input: { schema: "query:string" }
    output: { schema: "items:list" }
  capabilities_required: ["network"]
  security:
    seccomp_profile: "default-restrictive"
    cgroup: "tool-low"
  signatures:
    cosign: "sigstore://..."


⸻

5) Scheduler (Preemptive + Quotas)
•Queues: high, normal, low با وزن‌ها در config/scheduler.yaml
•Preemption: اگر job با priority بالاتر برسد، job جاری checkpoint می‌شود (snapshot در Redis/MinIO)
•Quotas: بر اساس tenant/agent (max_concurrency, token_rate, usd_per_hour)
•Backpressure: با Redis Streams یا PriorityQueue در حافظه + persistent journal

نمونه‌ی اسکلت:

# /kernel/scheduler.py
import time, heapq
class Scheduler:
    pq = []  # (priority, ts, task)
    @classmethod
    def submit(cls, task, tenant):
        item = (task["priority"], time.time(), task)
        heapq.heappush(cls.pq, item)
        return {"enqueued": True, "size": len(cls.pq)}
    @classmethod
    def next(cls):
        if not cls.pq: return None
        return heapq.heappop(cls.pq)[2]

در عمل: به Redis Streams + workerهای async تبدیل می‌شود؛ preemption با checkpoint در /kernel/memory.

⸻

6) Memory سلسله‌مراتبی + RAG

پیکربندی

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

کلیدها/کالکشن‌ها
•Redis: mem:{tenant}:{agent}:{task}:{key}
•Qdrant: collection aion_long_memory (payload: tenant, agent, tags, ts)
•MinIO: episodic/{tenant}/{agent}/{day}/{uuid}.jsonl

RAG API

POST /v1/memory/query
{ "type":"long", "knn": { "text":"...", "k":8 }, "filter":{"tenant":"...","agent":"..."} }


⸻

7) Sandbox & Security
•seccomp: kernel/sandbox/seccomp_profile.json (deny-by-default، allow minimal syscalls)
•cgroup: kernel/sandbox/cgroup_profiles.yaml (cpu/mem/gpu quotas)
•eBPF probes: latency/IO anomalies → ارسال به Prometheus
•HMAC برای Syscall: Header X-SIG-HMAC (sha256) با secret tenant
•Cosign: امضای agent.yml و tool.yml + SBOM در CI

⸻

8) Policy Brain + SafeKeeper
•Brain: سرویس کوچکی که از آمار Router/Scheduler/Memory، پیشنهاد policies/ جدید می‌سازد (LLM محلی: Ollama/vLLM)
•SafeKeeper: health gates (p95 latency, error_rate, cost/hour) → در صورت انحراف rollback به policy_versions/{ver}

نمونه اینترفیس:

# /kernel/feedback.py
class PolicyBrain:
    @staticmethod
    def propose(snapshot: dict) -> dict:
        # run LLM prompt → new bundle
        return {"version": "2025-11-03-01", "changes": {...}}

    @staticmethod
    def rollback(version: str) -> dict:
        # atomically switch symlink → policies/current -> policies/policy_versions/{version}
        return {"rolled_back": version}


⸻

9) SDK نمونه (Python)

# /sdk/python/aion_sdk/agent.py
import os, requests, hmac, hashlib, json

class Agent:
    def __init__(self, agent_id, kernel_url, secret, tenant):
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


⸻

10) ارتقای Console (Next.js)
•مسیر جدید: /kernel با تب‌های:
•Agents (process table: agent_id, state, cpu, mem, gpu, queue, age)
•Memory (short/long/episodic usage + GC)
•Syscalls (live stream با WebSocket + filters)
•Scheduler (queue depth, p95, fairness)
•Policy (current/versions, diff, propose, rollback)
•ChatOps Terminal: /kernel/terminal با slash-commands:
/agent status, /syscall trace {agent}, /policy diff, /memory top

Backend WS: GET /v1/events/stream?topics=kernel.syscalls,kernel.scheduler,kernel.gc

⸻

11) Observability

Metrics (Prometheus):
•aion_kernel_scheduler_queue_depth{queue}
•aion_kernel_syscall_latency_ms{syscall}
•aion_kernel_preemption_count
•aion_memory_gc_events_total{kind}
•aion_policy_rollbacks_total
•aion_agent_heartbeats{tenant,agent}

Traces (OTel):
•span names: kernel.syscall, kernel.schedule, kernel.memory.query, kernel.policy.propose

⸻

12) CI/CD & امنیت Supply-Chain
•GitHub Actions:
•Build & Test: kernel + sdk + console pages
•Security: Trivy + SBOM (Syft)
•Cosign: sign agent/tool artifacts + verify in deploy job
•E2E: docker-compose core+kernel، سناریو Route→Syscall→Memory→Analytics

⸻

13) Compose تغییرات (نمونهٔ سرویس Kernel)

# docker-compose.kernel.yml
services:
  aion-kernel:
    build: ./kernel
    environment:
      - AION_KERNEL_PORT=8010
      - REDIS_URL=redis://redis:6379/3
      - QDRANT_URL=http://qdrant:6333
      - MINIO_URL=http://minio:9000
      - OLLAMA_URL=http://llm:11434
      - POLICY_DIR=/policies
    ports:
      - "8010:8010"
    depends_on: [redis, qdrant, minio]


⸻

14) جدول Services × Ports × Env (خلاصه)

ServicePortKey ENV
Console3000NEXT_PUBLIC_CONTROL_URL, NEXT_PUBLIC_KERNEL_URL
Gateway8080AION_GATEWAY_*
Control8001AION_CONTROL_*, DB/Redis/Kafka/Qdrant/MinIO
Kernel8010REDIS_URL, QDRANT_URL, MINIO_URL, POLICY_DIR
vLLM (opt)8008MODEL_*
Kafka/CH/etc.…KAFKA_BROKERS, CLICKHOUSE_URL


⸻

15) تست‌های پذیرش (Acceptance)
1.Syscall round-trip: Agent→/v1/syscall/tool.invoke→Tool→Result (≤ p95 2.5s)
2.Scheduler preemption: ارسال job high-priority و قطع منصفانهٔ job جاری با checkpoint
3.Memory RAG: put→query (KNN)→نتیجه با filter tenant/agent صحیح
4.Capability enforcement: Agent بدون network نتواند tool:web_search را invoke کند
5.Policy Brain propose + rollback: تولید نسخهٔ جدید + rollback خودکار در انحراف KPI
6.Console Kernel pages: نمایش زندهٔ queue depth, syscalls, memory usage, traces
7.OTel/Grafana: متریک‌ها و نمودارها بالا بیاید؛ لاگ ساختاریافته

⸻

16) نمودار Sequence (Mermaid)

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


⸻

17) نمونهٔ حداقلی Agent (Python)

# examples/agents/researcher/main.py
from aion_sdk.agent import Agent
agent = Agent(agent_id="agent://tenantA/researcher-1",
              kernel_url="http://localhost:8010",
              secret="TENANT_A_SECRET",
              tenant="tenantA")

res = agent.syscall("tool.invoke", {"tool":"web_search","query":"AION-OS Kernel"})
print(res)


⸻

نتیجه

با این ارتقا:
•Kernel حقیقی + syscall + context/memory درون‌سازمانی (مانند AIOS) را داریم،
•اما مقیاس توزیع‌شده، سیاست‌محوری/امنیت سازمانی، و لایهٔ دادهٔ بزرگ AION-OS را هم حفظ و تقویت می‌کنیم—بنابراین نه‌تنها هم‌تراز AIOS، بلکه برتر از آن برای سناریوهای تولیدی و Enterprise خواهیم بود.

⸻

PR محتویات پیشنهادی
•kernel/ (کد بالا + اسکلت‌ها)
•sdk/python/aion_sdk/ + sdk/ts/aion-sdk/
•config/kernel.yaml, config/memory.yaml, config/scheduler.yaml
•policies/agent.capabilities.yaml + policies/policy_versions/ (نمونه)
•docker-compose.kernel.yml
•console/app/(kernel)/{agents,syscalls,memory,policy,terminal}/page.tsx (اسکلت)
•tests/e2e/kernel/{syscall_roundtrip.test.py, scheduler_preempt.test.py, memory_rag.test.py}
•docs/aion_kernel_upgrade_plan.md (همین فایل)
