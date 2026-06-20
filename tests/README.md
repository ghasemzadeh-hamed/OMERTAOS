# Test strategy

OMERTAOS uses a test pyramid with service-local unit tests, contract tests at every boundary, integration tests against real dependencies, and a small end-to-end suite through Console/Gateway. Tests must be deterministic, tenant-isolated, parallel-safe, and emit useful artifacts without secrets.

| Suite | Scope |
|---|---|
| Unit | Pure planning, routing, policy, adapters, middleware, grant validation and sandbox helpers |
| Integration | gRPC/HTTP contracts, databases, Redis Streams, registry/policy loading and migrations |
| Architecture | Import/dependency rules, forbidden Console→Control access, no Python subprocess execution, canonical directory ownership |
| Gateway | Auth/RBAC, validation, status mapping, streams, deadlines, breaker and CORS |
| Rate limiting | Principal/tenant/IP keys, atomic windows, expiry, concurrency and fail behavior |
| Idempotency | Same-key replay, body mismatch, concurrent reservation, TTL, backend timeout and tenant isolation |
| Runtime | Grant denial, namespaces/cgroups/seccomp, path/network constraints, timeouts, cancellation, output limits and cleanup |
| End-to-end | Submit → plan → policy → runtime → events → result, including failure/retry/cancel paths |

Unit tests mock only the immediate port. Integration tests use disposable containers and seeded versioned fixtures. Runtime security tests run on compatible isolated CI workers and must verify negative cases. Load tests measure admission latency, streaming fan-out, queue age, scheduler fairness and Runtime saturation with explicit thresholds.

## CI flow

1. Format, lint, type-check, secret scan, and schema/breaking-change validation.
2. Run Python, TypeScript and Rust unit tests in parallel.
3. Generate bindings and run contract plus architecture-boundary tests.
4. Start ephemeral Postgres, MongoDB, Redis, Qdrant, MinIO, Control, Gateway and Runtime; run integration tests.
5. Run sandbox/security suites on privileged dedicated runners, then smoke/end-to-end tests.
6. Build images, scan them, and publish JUnit, coverage, traces/logs and benchmark deltas.

Failures must preserve sanitized service logs and Compose state. Flaky retries are diagnostic only and cannot convert a failing required check into success. Coverage is tracked by risk and changed code; policy, authorization, state transitions, retry safety and capability enforcement require branch/negative-path coverage.
