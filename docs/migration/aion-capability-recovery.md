# AION capability recovery plan

The redesign is delivered in vertical slices. Each slice includes schema, policy,
persistence, API, audit, tests, documentation and rollback notes.

## Gate 0: repository truth and quickstart

- Keep Runtime buildable and healthy on gRPC port 50051.
- Align architecture tests with canonical paths.
- Replace wrappers that import removed modules.
- Validate Console, Gateway, Control and Runtime together.
- Quarantine broken symlinks, rejected patches and legacy Compose definitions;
  do not delete them.

Exit: quickstart is healthy and canonical import probes pass.

## Gate 1: task execution spine

- Versioned task/workflow schemas and state transitions.
- Postgres task/attempt/outbox repositories with additive migrations.
- Redis-backed lease queue with priority, retry budget, deadline and fencing token.
- Control Runtime client with deadlines and signed grants.
- Runtime cancellation, bounded output and auditable terminal result.

Exit: one tenant-scoped task runs end-to-end with trace and deterministic retry.

## Gate 2: agent, model and prompt registries

- Agent manifests and tenant-visible lifecycle API.
- Canonical model loader/router using `registry/models/`.
- Prompt versions, evaluations, activation and rollback metadata.
- Console catalog and My Agents consume real Gateway APIs.

Exit: task records pin immutable agent/model/prompt versions.

## Gate 3: governance, policy and observability

- Signed identity context, RBAC/ABAC and data classification.
- Approval service for critical actions.
- Persistent audit sink and OpenTelemetry propagation.
- Rate-limit/idempotency regression tests and tenant-isolation tests.

Exit: unauthorized/cross-tenant/tool-escalation scenarios are denied and audited.

## Gate 4: RAG, memory and multimodal

- Canonical adapters under `data/`; legacy wrappers forward to them.
- Upload, normalize, classify, chunk, embed, retrieve and cite pipeline.
- Tenant/ACL filters in every retrieval query.
- Short-term and retained memory with policy-driven TTL/deletion.
- Document/image/table/audio processors emitting one normalized envelope.

Exit: permission-aware answers cite stored sources and pass leakage tests.

## Gate 5: no-code automation and integrations

- Versioned automation graph, validator and orchestration compiler.
- Trigger/action registry, scheduler and approval nodes.
- Workflow Designer backed by real run/event APIs.
- Consolidated Windows bridge and registered local-vLLM provider.

Exit: an uploaded spreadsheet can trigger an approved, audited workflow end-to-end.

## Gate 6: cleanup and production readiness

- Compare and migrate unique content from legacy roots.
- Regenerate protobuf bindings from one source contract.
- Test backup/restore and document RPO/RTO.
- Validate Kubernetes, observability and headless bundles.
- Remove legacy paths only in separately reviewed changes with upgrade notes.

