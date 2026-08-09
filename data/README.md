# Data Layer

**Document role:** canonical ownership and design contract. Adapter presence
does not by itself demonstrate every storage workflow, cross-store recovery, or
tenant-isolation property described below.

The Data Layer provides typed, tenant-aware persistence and retrieval interfaces. It prevents orchestration code from depending on vendor clients and assigns each store a specific role.

| Store | Role |
|---|---|
| Postgres | Authoritative relational state, transactions, task/attempt metadata, outbox |
| MongoDB | Flexible versioned documents such as plans and rich results |
| Redis | Ephemeral cache, idempotency, leases, queues, and Streams |
| Qdrant | Embeddings and filterable vector references |
| MinIO | Large immutable inputs, outputs, datasets and artifacts |

Adapters implement domain ports such as `TaskRepository`, `DocumentRepository`, `Cache`, `VectorIndex`, `ObjectStore`, and `EventLog`. A unified unit-of-work coordinates only operations supported by one transactional boundary; it does not claim distributed ACID across databases.

Shared adapter, repository, unit-of-work and health contracts live in
`data/interfaces/`. The migration-era data roots were retired in Structure S5;
all imports and implementations must use `data/`.

The RAG pipeline authorizes ingestion, normalizes and classifies content, chunks it, generates versioned embeddings, stores source objects in MinIO, writes metadata in Postgres, and upserts vectors plus tenant/ACL filters in Qdrant. Query uses the matching embedding model, mandatory filters, top-k retrieval, optional reranking, source hydration, and provenance emission.

All calls require tenant and actor/service context. Raw database clients stay inside adapters. Parameterized operations, encryption, retention labels, least-privilege service accounts, redacted telemetry, and explicit consistency requirements are mandatory. Cross-store updates use outbox/saga and reconciliation, not best-effort dual writes.
