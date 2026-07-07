# AION canonical design

This document is the implementation contract for the AION redesign. When older
plans disagree, this document and `STRUCTURE.md` take precedence.

## Service ownership

| Plane | Owns | Must not own |
|---|---|---|
| Console | presentation, accessibility, RTL/i18n, browser session | credentials, policy decisions, direct database calls |
| Gateway | authentication, coarse authorization, rate limits, idempotency, public HTTP/SSE/WS | planning, model choice, tool execution |
| Control | task/workflow state, agent/model selection, policy decisions, scheduling, aggregation | arbitrary subprocess or sandbox implementation |
| Runtime Daemon | grant verification, sandbox, tool/process execution, resource enforcement | user authentication, planning, tenant business policy |
| Data | typed persistence, transactions, retrieval and retention | HTTP routes and orchestration decisions |
| Registry | immutable agent/model/prompt metadata and lifecycle state | model invocation and task execution |
| Policies | versioned human-authored rules and evaluator interfaces | request transport and storage implementation |
| Schemas | source protobuf, JSON Schema and event contracts | service business logic |

## Canonical repository map

```text
console/
gateway/
control/
  agents/
  automation/
  governance/
  orchestration/
  runtime/
  scheduling/
runtime-daemon/
data/
  adapters/
  memory/
  rag/
  vector/
registry/
  agents/
  models/
  prompts/
  schemas/
policies/
schemas/v1/
shared/
deploy/
integrations/
tests/
```

Missing directories in this map are target modules, not permission to add empty
parallel frameworks. They are created only with a working capability slice.

## Request and execution flow

1. Gateway authenticates the principal and produces a signed tenant-aware context.
2. Control validates the versioned request and writes task state plus an outbox event.
3. Orchestration decomposes the goal and resolves immutable agent/model versions.
4. Governance evaluates data class, budget, tool and approval constraints.
5. Scheduler leases an attempt using a fencing token and deadline.
6. Control mints a signed, narrow Runtime grant and calls Runtime over gRPC.
7. Runtime validates the grant, executes inside the sandbox and emits bounded events.
8. Control persists events idempotently, stores large artifacts in MinIO and closes
   the task with a monotonic terminal state.

## Persistence ownership

| Store | Canonical use |
|---|---|
| Postgres | tenants, identities, registry lifecycle, workflows, tasks, approvals, outbox |
| Redis | rate limits, ephemeral coordination, leases, streams and cache |
| MongoDB | flexible run/tool documents only where relational storage is unsuitable |
| Qdrant | embeddings plus tenant/ACL-filterable references; never canonical documents |
| MinIO | uploads, normalized documents, artifacts, model/dataset objects |

Every persisted row/document must carry tenant scope where applicable. Cross-tenant
queries require an explicit system scope and an audit event.

## Registry design

- `registry/models/` is the only writable source for model profiles.
- `registry/agents/` stores immutable agent-version manifests and capability needs.
- `registry/prompts/` stores immutable prompt versions and evaluation references.
- Root `models/` remains a compatibility mirror until all callers move; CI checks
  that mirrored files do not diverge.
- Secrets are references such as `secret://...`, never values in manifests.

## Orchestration and automation

No-code automation is not a separate executor. Its versioned graph is validated and
compiled into the same orchestration workflow representation used by API workflows.
Triggers create normal tenant-scoped runs; actions use normal agent/tool policies;
approval nodes use the governance approval service.

## Security invariants

- Default deny for tools, filesystem, network, subprocess, devices and GPU.
- Signed identity propagation and signed Runtime grants with audience, expiry,
  task/attempt IDs, lease token and resource ceilings.
- Prompt injection signals can narrow or stop a plan but never grant capability.
- Uploads are size/type checked, malware scanned, classified and stored before use.
- Secrets and raw confidential content are redacted from logs and event payloads.
- Critical actions require explicit approval and are not auto-retried after an
  uncertain side effect.

## Compatibility and cleanup

Legacy roots remain read-only migration sources. A legacy path can be removed only
after imports, runtime references, Git history, generated-source status, tests,
upgrade notes and rollback steps are documented. Compatibility wrappers must point
from legacy to canonical code, never from canonical code into a deleted legacy tree.

