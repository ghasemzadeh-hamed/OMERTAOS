# AION capability audit

Status date: 2026-07-05. This audit is based on the checked-out `AION` branch,
runtime probes, import probes, Compose validation, and Git history. It separates
implemented behavior from design-only documentation.

## Executive finding

The platform is not missing one isolated module. It contains several architecture
generations at once. The Console exposes more product surfaces than the canonical
Control implementation supports, while compatibility modules still import the
removed `control.os` package. Git commit `5fa2b9c0` deleted the former Control
implementation, including agent catalog, RAG, memory, model, security, registry,
and admin APIs. Those implementations remain recoverable from history but must be
migrated selectively; restoring the entire old tree would recreate two sources of
truth.

The only supported direction for new work is:

```text
Console -> Gateway -> Control -> Runtime Daemon
                         |
              Data / Registry / Policies

All boundaries use versioned contracts from schemas/ and generated clients from shared/.
```

## Capability matrix

| Capability | Evidence in current tree | Current state | Canonical owner | Recovery decision |
|---|---|---|---|---|
| Quickstart | `docker-compose.quickstart.yml` | Operational for Runtime; full-stack smoke still required | `deploy/` plus root entrypoint | Keep root entrypoint thin and tested |
| Control API | `control/app/main.py` has health, task-status placeholder, network proxy API | Partial | `control/` | Port selected historical endpoints into domain routers; do not restore `control/os` |
| Runtime | Rust service, gRPC server, Docker image and readiness probe | Buildable; execution adapters are still placeholders | `runtime-daemon/` | Complete grant verification, sandbox and lifecycle behind the existing proto |
| Control to Runtime | Gateway points at Control gRPC; Control has no canonical Runtime client | Missing | `control/runtime/` | Generate a client from the canonical Runtime proto and require deadlines/grants |
| Multi-tenancy | Tenant headers in network routes; design docs describe isolation | Partial and header-trusting | Gateway identity plus Control policy | Signed tenant context, tenant-scoped repositories, quotas and tests |
| Agent registry | `agents/` is empty; former catalog is recoverable from Git history | Missing | `registry/agents/` metadata; `control/agents/` lifecycle | Add versioned manifests, persistent instances and tenant visibility |
| Model registry | Identical YAML exists in `models/` and `registry/models/`; four Moonshot profiles use an older unversioned schema | Canonical read API restored; metadata still duplicated | `registry/models/` | Normalize old profiles as `legacy-unversioned`, add routing/lifecycle, migrate metadata, keep root `models/` read-only compatibility |
| Orchestration | `orchestration/dag.py` and `scheduler.py` are small in-memory primitives | Prototype | `control/orchestration/` using reusable primitives | Add durable workflow/task state, retries, approvals and event emission |
| Scheduler/queue | Scheduler prototype plus bounded `control.task_queue` compatibility queue | Development-only | `control/scheduling/` | Durable tenant-partitioned leases; in-memory implementation remains tests/dev only |
| Event bus | Local bus works; Kafka methods raise `NotImplementedError` | Prototype | `eventbus/` contract, Control outbox | Redis Streams default; Kafka adapter optional; never fire-and-forget durable facts |
| Policies/governance | Capability helper and design docs exist | Prototype | `policies/` definitions, Control decision point, Runtime enforcement | Versioned decisions and signed least-privilege grants |
| Audit/observability | Audit returns an in-memory dataclass only | Prototype | `observability/` interfaces plus append-oriented sink | Persist task, tool, model, admin and policy events with trace IDs |
| RAG/data | Functional-looking files duplicated across `data/` and `database/` | Duplicated, not end-to-end wired | `data/` | Preserve compatibility imports while callers move to tenant/ACL-aware adapters |
| Memory | Historical routes exist only in Git history | Missing | `data/memory/`, orchestrated by Control | Separate short-term state from retained knowledge and enforce retention policy |
| Multimodal | Console upload surfaces exist; no canonical processing service | Missing | `control/media/` coordination plus isolated processors | Normalize outputs before RAG; scan and classify every upload |
| No-code automation | Workflow designer UI exists; backend workflow runtime does not | UI-only | `control/automation/` | Versioned graph schema compiled into orchestration workflows |
| Windows bridge | Two trees exist under `integrations/` and `execution/` | Duplicated | `integrations/windows-agentic-bridge/` | Diff and migrate unique assets; no direct deletion |
| Local inference | `docker-compose.vllm.yml` exists | Optional, incompletely integrated | `deploy/` plus model registry | Register as a local provider and route through policy/model health |
| Backup/restore | Assets are scattered in deployment/legacy trees | Unverified | `deploy/operations/` | Inventory, document RPO/RTO, and test restore before cleanup |
| i18n/RTL | English/Farsi messages and RTL hooks exist | Partial | `console/` | Add route-level coverage and eliminate hard-coded UI strings incrementally |

## Confirmed defects

1. `control/models/registry.py`, `models/registry.py`, `control/schemas/*`,
   `schemas/v1/*`, and retention wrappers import the absent `control.os` package.
2. Architecture tests still treat `control-plane/` and `rust-runtime/` as the
   primary implementations, contradicting `STRUCTURE.md`.
3. `control/task_queue.py` is imported by tests but does not exist.
4. Gateway exposes/falls back for model and setup routes that canonical Control
   does not implement.
5. The optional `dev-kernel` Compose profile references a missing Dockerfile.
6. `process-analytics` is a broken symlink and must remain quarantined until its
   historical target is reconciled.
7. `registry/__init__.py.rej` is a rejected-patch artifact, not executable source.

## Validation snapshot

- Canonical architecture, model/schema bridges, queue, model API and network proxy
  tests: 20 passed with 95% coverage over the redesigned Python modules.
- Primary Quickstart, Local and root Compose configuration parsing: pass.
- Runtime image build and readiness: pass.
- Full Python suite collection: blocked by 11 historical test modules importing
  removed `os.control.os`, `os.kernel`, `aion`, or `cli.main` packages. These tests
  are retained as recovery requirements and are not silently skipped.
- Control and Runtime images build; Control image smoke returned health and all 11
  model profiles; Runtime reached healthy and its stopped-state probe failed closed.
- Full Quickstart startup is not yet proven because Docker Hub returned EOF while
  resolving the Mongo image. Console/Gateway/data-service runtime smoke remains open.

## Safety constraints

- Do not delete legacy directories, model copies, generated protobufs, symlinks,
  or deployment trees during recovery.
- Do not restore `control/os` as a second service implementation.
- Do not trust tenant IDs supplied directly by browsers.
- Do not let Control execute shell/process operations; Runtime remains the only
  privileged execution boundary.
- Do not claim a capability is complete until its API, policy, persistence,
  audit, tests, and UI path have all been exercised.
