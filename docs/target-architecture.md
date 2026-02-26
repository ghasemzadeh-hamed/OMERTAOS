# OMERTAOS Target Architecture (Kernel / Control / Data Planes)

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


This document defines the **target-state architecture** for OMERTAOS to eliminate duplication, enforce layer boundaries, and enable enterprise-scale multi-team development.

## Objectives

- Zero duplication for core orchestration concerns.
- Zero cross-layer runtime violations.
- Clear separation of Kernel / Control / Data responsibilities.
- Single RAG engine interface and implementation flow.
- Single AI Router entrypoint.
- Single Model Runtime abstraction.
- Secure, sandboxed plugin execution.
- Multi-tenant and enterprise scalability.

## Architecture Planes

OMERTAOS is organized into five planes:

1. **Kernel Plane**: execution, scheduling, orchestration, runtime, sandboxing.
2. **Control Plane**: policy, governance, registry metadata, APIs, audit.
3. **Data Plane**: memory, vector, embeddings, retrieval pipelines.
4. **Service Plane**: domain services (analytics, registry services, management services).
5. **Interface Plane**: gateway/UI/CLI/SDK for system consumers.

## Proposed Repository Topology

```text
omertaos/
├── kernel/
│   ├── core/
│   ├── router/
│   ├── scheduler/
│   ├── runtime/
│   ├── sandbox/
│   └── multitenant/
├── control/
│   ├── api/
│   ├── governance/
│   ├── registry/
│   ├── policy/
│   └── audit/
├── data/
│   ├── rag/
│   ├── vector/
│   ├── memory/
│   └── storage/
├── services/
│   ├── model-registry/
│   ├── agent-manager/
│   ├── capability-service/
│   └── analytics/
├── interface/
│   ├── gateway/
│   ├── console/
│   ├── cli/
│   └── sdk/
├── shared/
│   ├── contracts/
│   ├── events/
│   ├── types/
│   ├── utils/
│   └── exceptions/
└── infra/
    ├── docker/
    ├── k8s/
    ├── observability/
    └── migrations/
```

## Single AI Router Rule

Only one router is allowed as authoritative runtime router:

- `kernel/router/ai_router.py`

Responsibilities:

- model selection
- tool routing
- agent routing
- capability resolution

Control plane may expose metadata and configuration for routing, but **must not execute runtime routing logic**.

## Single RAG Rule

RAG is centralized under Data Plane:

- `data/rag/`
- `data/vector/`

Recommended modules:

- `retriever.py`
- `reranker.py`
- `pipeline.py`
- `embedding.py`

All consumers use shared contracts (ports), for example:

```python
class RAGEngine(Protocol):
    def retrieve(self, query: str) -> list[Document]:
        ...
```

## Kernel and Control Separation Rules

Golden boundary:

- `kernel` must not import control runtime internals.
- `control` must not host execution runtime logic.

Kernel scope:

- execution
- scheduling
- isolation
- orchestration

Control scope:

- CRUD/config/policy/audit/metadata

## Plugin Security Model

Plugin runtime belongs to:

- `kernel/sandbox/`

Each plugin package should include:

```text
plugins/
  plugin.yaml
  main.py
  permissions.yaml
```

Enforcement before load:

- signature check
- capability check
- policy enforcement

Runtime constraints:

- isolated container execution
- capability-based permissions
- resource limits
- IPC via constrained interfaces (e.g., gRPC)

## Dependency Rules (Strict)

Allowed:

- `interface → control`
- `interface → services`
- `control → services`
- `services → data`
- `kernel → data`
- `kernel → shared`

Forbidden:

- `data → kernel`
- `services → kernel`
- `control → kernel runtime`

## Event Backbone

Shared events belong to `shared/events`, e.g.:

- `AgentCreated`
- `ModelLoaded`
- `PolicyUpdated`
- `PluginInstalled`

Inter-plane coordination should prefer asynchronous event-driven flows.

## Testing and CI Expectations

Architecture checks should live under:

```text
tests/
  unit/
  integration/
  architecture/
```

Architecture checks should include:

- circular dependency detection
- layer violation detection
- forbidden import detection

CI should fail on architecture boundary violations.

## Migration Guidance

This document is a target-state contract. Existing modules can be migrated gradually by:

1. adding compatibility shims,
2. moving runtime logic into kernel/data/service boundaries,
3. enabling architecture tests in blocking mode once migration milestones are complete.

## Runtime Daemon Integration

OS-level resource isolation and command execution are implemented in `runtime-daemon/` and invoked via `control_plane/runtime_client.py` using `shared/proto/runtime.proto`.

