# Architecture & Design

## High-Level Architecture
```mermaid
flowchart LR
  subgraph Client
    Console[Web Console]
    CLI[CLI/Automation]
    SDKs[SDKs]
  end
  subgraph Edge
    Gateway[Gateway API & Auth]
  end
  subgraph ControlPlane[Control Plane]
    Control[aion Control Service]
    Scheduler[Kernel Schedulers]
    Policies[Policy Engine]
  end
  subgraph Data
    Postgres[(Postgres)]
    Redis[(Redis/Cache)]
    Qdrant[(Qdrant/Vector)]
    MinIO[(MinIO/Object Store)]
    Kafka[(Kafka Events)]
  end
  subgraph Observability
    OTEL[(OTEL Collectors)]
    Prometheus[(Prometheus)]
    Grafana[(Grafana)]
  end
  Client -->|HTTPS/WS/gRPC| Gateway
  Gateway -->|AuthZ, Routing| Control
  Control -->|Model/Agent Ops| Scheduler
  Control -->|Policies & Catalog| Policies
  Control <-->|State| Postgres
  Control <-->|Caches| Redis
  Control -->|Vectors| Qdrant
  Control -->|Artifacts| MinIO
  Control -->|Events| Kafka
  Kafka -->|Traces/Metrics| OTEL
  Gateway -->|Metrics| Prometheus
  OTEL --> Grafana
  Prometheus --> Grafana
```

## Context & Boundaries
```mermaid
flowchart TB
  subgraph OMERTAOS
    Gateway
    Control
    Console
    Schedulers[Kernel + Runtime Nodes]
  end
  Users[(Operators/DS/Developers)] -->|Browser/CLI| Gateway
  Console --> Gateway
  Gateway --> Control
  Control --> Schedulers
  Control <-->|IdP| IdP[(OIDC/SAML)]
  Control <-->|Secrets| Vault[(Secret Store)]
  Control <-->|Logs/Events| SIEM[(Logging/SIEM)]
  Control <-->|Tickets| ITSM[(Support/ITSM)]
  Control <-->|Registry Sync| OCI[(OCI/ORAS Registry)]
  Control <-->|Model Hosting| ExternalLLM[(External LLM APIs)]
```

## Component / Module Diagram
```mermaid
flowchart LR
  Gateway --- AuthN[AuthN/Z Middleware]
  Gateway --- API[REST/gRPC Proxy]
  Gateway --- RateLimit[Rate Limiter]
  Control --- TaskMgr[Task Orchestrator]
  Control --- Policy[Policy Evaluation]
  Control --- AgentSvc[Agent Catalog & Lifecycle]
  Control --- RegistrySync[Model/Tool Registry Sync]
  Control --- Telemetry[Metrics/Tracing Emitters]
  Scheduler --- KernelRT[Runtime Executors]
  Scheduler --- Sandboxing[Sandbox & Quotas]
  DataStores[(Postgres/Redis/Qdrant/MinIO)]
  Observability[(OTEL/Prometheus/Grafana)]
  Gateway --> Control
  Control --> Scheduler
  Control --> DataStores
  Gateway --> Observability
  Control --> Observability
```

## Sequence Diagrams
### Login (OIDC)
```mermaid
sequenceDiagram
  participant U as User
  participant UI as Console
  participant G as Gateway
  participant IDP as Identity Provider
  participant C as Control
  U->>UI: Access console
  UI->>IDP: Redirect for login (OIDC)
  IDP-->>UI: Auth code + tokens
  UI->>G: Exchange token + session establish
  G->>C: Introspect/verify token
  C-->>G: Claims + tenant context
  G-->>UI: Session cookie / JWT
```

### Agent Deployment
```mermaid
sequenceDiagram
  participant U as Operator
  participant UI as Console/CLI
  participant G as Gateway
  participant C as Control
  participant K as Kernel Scheduler
  participant DS as Data Stores
  U->>UI: Submit new agent spec
  UI->>G: POST /agents with manifest
  G->>C: Forward request with authz
  C->>C: Validate schema + policies
  C->>DS: Persist agent + config
  C->>K: Schedule deployment
  K-->>C: Deployment status
  C-->>G: Success + agent id
  G-->>UI: Deployment confirmation
```

### Job Execution
```mermaid
sequenceDiagram
  participant U as Client
  participant G as Gateway
  participant C as Control
  participant K as Kernel Runtime
  participant Q as Queue/Kafka
  participant DS as Data Stores
  U->>G: POST /tasks (intent)
  G->>C: Authorize + route
  C->>C: Resolve agent/model
  C->>K: Dispatch task
  K-->>C: Stream progress
  C->>Q: Emit events/metrics
  C->>DS: Persist outputs/artifacts
  C-->>G: TaskResult
  G-->>U: Response
```

## Domain Model / ERD
```mermaid
erDiagram
  TENANT ||--o{ USER : scopes
  TENANT ||--o{ AGENT : owns
  TENANT ||--o{ POLICY : governs
  USER ||--o{ TASK : submits
  AGENT ||--o{ TASK : executes
  TASK ||--o{ RUN : histories
  RUN ||--|{ ARTIFACT : produces
  MODEL ||--o{ AGENT : referenced
  POLICY ||--o{ ENFORCEMENT : applies
  ENFORCEMENT ||--|| TASK : validates
```

## Design Patterns
- **Gateway proxy + BFF**: isolates auth/routing and provides console-friendly APIs.
- **Control-plane / data-plane split**: orchestrator delegates execution to kernel runtimes.
- **CQRS-style separation**: read/write paths segregated via caches and event streams.
- **Policy-as-code**: policy engine evaluates manifests and tenant context before actions.
- **Event-driven telemetry**: Kafka/OTEL streams decouple producers from analytics consumers.

## Security Architecture
- **TLS everywhere** with mutual TLS between gateway, control, and runtimes.
- **Authentication** via OIDC/SAML for console; API keys/JWT for service-to-service.
- **Authorization** using RBAC/ABAC tied to tenant context; rate limiting at gateway.
- **Secrets management** delegated to external vault; no secrets stored in code.
- **Data protection**: encryption in transit (TLS) and at rest (KMS-backed storage for Postgres/MinIO); scoped caches per tenant.
- **Auditability**: audit logs for login, policy changes, agent lifecycle, and task execution emitted to SIEM.

## Logging, Metrics, and Tracing
- **Tracing**: OTEL instrumentation in gateway/control publishes spans to collectors.
- **Metrics**: Prometheus scrapes gateway/control/kernel exporters; Grafana dashboards for latency, throughput, and resource use.
- **Logging**: structured JSON logs shipped to centralized log store/SIEM with correlation IDs.
- **Alerting**: SLO-based alerts on error rates, P95 latency, scheduler backlog, and failed policy checks.

## Architecture Decision Records (ADRs)
- **WASM-first strategy** for execution sandboxes (`docs/adr/0001-wasm-first.md`).
- **Kafka requirement** for eventing backbone (`docs/adr/0002-kafka-required.md`).
- **Public gRPC interfaces** to standardize module communication (`docs/adr/0003-public-grpc.md`).
- **Multi-tenant uplift** with tenant-scoped resources and headers (`docs/adr/0004-multi-tenant-uplift.md`).
- **ORAS packaging** for artifacts and manifests (`docs/adr/0005-oras-packaging.md`).
