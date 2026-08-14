# OMERTAOS (AIONOS) Structural Audit and Production Refactor Plan

> Historical plan. Its recommendation to make `control-plane/` and
> `rust-runtime/` canonical is superseded by
> `docs/adr/0001-canonical-aion-ownership.md`. It remains as audit history and
> must not be used as the current implementation contract.

## 1) Structural Violation Report

### Critical findings
- **Duplicate deployment payloads** exist in both `deploy/` and `execution/` (`bundles`, `compose`, `k8s`, `observability`, `scripts`, `systemd`, `windows`) which introduces config drift risk and release inconsistency.
- **Layer naming drift** (`control/` and `control-plane/`; `data/`, `database/`, and `db/`) indicates mixed architecture generations.
- **Transport/business blending** likely exists where API/service modules are mixed with orchestration/runtime concerns (detected from repo topology and current boundary tests scope).
- **Multiple config sources** are spread across top-level `config/`, `deploy/headless-bundle/config/`, app-local config files, and compose variants.
- **CI workflow fragmentation** previously had seven overlapping workflows with inconsistent branch targets (`main`, `develop`, `AION`) and duplicated responsibilities.
- **Rejected patch artifacts (`*.rej`)** were committed in `tests/architecture/` (now removed).

### Detected architecture violations to enforce
- Domain layer must not import gateway/control transport modules.
- Gateway layer must not import direct database adapters.
- Execution layer must not include API transport logic.
- Control-plane access to OS process primitives must be routed via runtime client abstraction only.

## 2) REMOVE (not for production)

- `tests/architecture/*.rej`  
  **Reason:** rejected patch residue committed into source tree.  
  **Impact:** confuses architecture contract history; may mislead tooling.
- `console/node_modules/`, `gateway/node_modules/` (if tracked in Git history/state)  
  **Reason:** generated dependencies should not ship in source control.  
  **Impact:** bloated repository and noisy diffs.
- Duplicated deployment trees under `execution/*` mirroring `deploy/*`  
  **Reason:** execution engine should not host packaging/distribution manifests.  
  **Impact:** severe drift risk for prod rollout.
- Legacy/parallel roots (`control/` once migration to `control-plane/` is complete)  
  **Reason:** split control-plane code paths create ambiguous runtime ownership.  
  **Impact:** duplicated logic and onboarding friction.

## 3) Refactor mapping (violations → target)

| Violation | Problem | Refactor plan | Target folder |
|---|---|---|---|
| Deployment assets inside runtime layer (`execution/compose`, `execution/k8s`, etc.) | runtime engine coupled to packaging | move all packaging/manifests to `deploy/`; keep execution only process/task runtime | `deploy/*` |
| Multiple control roots (`control/` vs `control-plane/`) | fractured control-plane contracts | consolidate APIs/schemas/services in `control-plane/`; archive or remove `control/` | `control-plane/` |
| Mixed DB abstractions (`data/`, `database/`, ad-hoc adapters) | schema and adapter drift | centralize repository interfaces in `db/interface.py`; keep concrete adapters in `db/adapters/*` and map legacy modules incrementally | `db/`, `database/` (migration bridge) |
| Service-to-service direct coupling | brittle synchronous dependencies | route cross-service notifications through event bus contracts | `eventbus/` |
| Kernel/runtime logic in Python layers | weak isolation boundary | move sandbox/capability enforcement to Rust kernel adapter modules with strict IPC | `rust-runtime/kernel-adapter/src` |

## 4) Target folder tree (clean architecture)

```text
ui/
gateway/
control-plane/
domain/
orchestration/
execution/
rust-runtime/
  kernel-adapter/
    src/
      cgroups.rs
      namespaces.rs
      seccomp.rs
      capabilities.rs
      process.rs
      sandbox.rs
      resource_limit.rs
      audit.rs
db/
  adapters/
    postgres/
    mysql/
    sqlite/
    mongo/
    redis/
    vector/
  interface.py
eventbus/
  interface.py
  local_bus.py
  kafka_bus.py
observability/
  logging/
  tracing/
  metrics/
  health/
  audit/
deploy/
schemas/
policies/
```

## 5) Rust module skeleton and responsibilities

Implemented module skeleton under `rust-runtime/kernel-adapter/src/`:
- `cgroups.rs`: cgroups v2 quota enforcement (CPU, memory, PID limits).
- `namespaces.rs`: mount/net/pid/user namespace isolation orchestration.
- `seccomp.rs`: default-deny syscall filter installation.
- `capabilities.rs`: capability drop to minimal profile.
- `process.rs`: process spawn bridge for sandboxed execution.
- `sandbox.rs`: compositional orchestration of all hardening controls.
- `resource_limit.rs`: typed resource quota contract.
- `audit.rs`: structured security audit events.

Security guarantees:
- Every spawned agent passes namespace + cgroup + seccomp + capability pipeline.
- Audit trail is mandatory for enforcement actions.
- Non-privileged execution baseline with capability minimization.

Performance notes:
- Tokio async runtime allows high concurrency for process supervision.
- Per-module isolation keeps hot path small and cache-friendly.
- IPC boundary avoids Python GIL bottlenecks for runtime-critical isolation logic.

## 6) CI/CD workflow repair delivered

Replaced fragmented workflows with:
- `ci.yml`: lint (Python/Rust), unit tests, integration stage, security scans (Bandit/Trivy/Cargo audit), docker multi-platform build, SBOM generation, conventional commit PR-title gate.
- `release.yml`: semantic version tag validation and automated release generation.

Branch protection policy (enforce in repo settings):
- Require PR review >=1.
- Require status checks from `CI / lint`, `CI / test`, `CI / security`, `CI / docker`.
- Require conversation resolution.
- Disallow force push on protected branches.

## 7) Event-driven core contracts

Events to standardize:
- `AgentInstalled`
- `AgentRemoved`
- `ModelLoaded`
- `PluginUpdated`
- `NodeJoined`
- `PolicyChanged`
- `ResourceLimitExceeded`

`eventbus/interface.py` defines the async bus contract and event envelope.

## 8) Zero-trust runtime model

Trust boundaries (text diagram):

```text
[User/UI] -> [Gateway/API AuthZ] -> [Control Plane Policy Engine] -> [Rust Runtime IPC]
                                                            -> [Event Bus]
[Rust Runtime IPC] -> [Sandboxed Agent Process]
[Sandboxed Agent Process] -X-> direct host syscall/cap escalation
```

Controls:
- Capability-based execution profile per agent.
- Signed plugin requirement + signature verification gate before load.
- Tenant-scoped quotas (CPU/memory/pids/network policy).
- Policy decision point in control-plane with enforcement point in runtime.
- Encrypted state at rest and RBAC-bound control API.

Attack-surface reduction:
- Remove direct service-to-service mutable calls in favor of immutable event contracts.
- Keep kernel-facing primitives in Rust adapter only.
- Block lateral movement via namespace/network segmentation.

## 9) Cluster federation model (enterprise)

```text
cluster/
  node/
  control/
  federation/
  scheduler/
  membership/
```

Design:
- Node agent registers with control plane over mTLS and signed join token.
- Membership + heartbeat tracked in distributed KV/event stream (NATS/Kafka-backed).
- Scheduler assigns workloads by quotas, affinity, and health score.
- Failure recovery via heartbeat timeout, workload requeue, idempotent replay events.
- Federation identity anchored in SPIFFE/SVID-style workload identity.

## 10) Migration plan to v1.0

1. **Freeze architecture contract** with CI gates (done via unified workflows).
2. **Consolidate duplicate deploy trees** and remove runtime-packaging overlap.
3. **Introduce DB abstraction boundary** and progressively redirect adapters.
4. **Migrate runtime-critical Python paths to Rust adapter** via IPC/gRPC.
5. **Enforce event-bus-only cross-service communication** for state changes.
6. **Enable mandatory audit/metrics/traces** for control and execution paths.
7. **Enterprise federation rollout**: mTLS join, scheduler, failover drills.

## 11) Deployment strategy

- **Lite:** single-node, SQLite, CPU-only, local event bus.
- **Professional:** PostgreSQL + optional GPU scheduling, multi-agent runtime.
- **Enterprise:** Kubernetes, distributed scheduler, Kafka/NATS, centralized policy + observability stack.

## 12) Risk analysis

- **High:** dual-source deployment definitions causing inconsistent runtime behavior.
- **High:** incomplete runtime isolation if any direct subprocess/system-call pathways bypass runtime client.
- **Medium:** schema sprawl across modules leading to serialization mismatches.
- **Medium:** weak release governance without branch protection + semantic version checks.

## 13) Performance bottleneck prediction

- Python orchestration path may bottleneck at high agent churn; mitigate with async queueing and Rust execution bridge.
- Excessive synchronous service chaining increases p99 latency; event-driven fan-out reduces tail latency.
- Multi-source config loading creates cold-start penalties and non-deterministic behavior; central config registry recommended.
