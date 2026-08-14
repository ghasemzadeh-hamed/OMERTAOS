# Gateway internal architecture

Fastify plugins form isolated composition units: configuration/secrets and telemetry load first; infrastructure clients and authentication decorators follow; admission middleware and route modules load last. Each plugin declares dependencies and closes its clients during server shutdown. Routes contain transport mapping only and call typed services.

```text
socket → request ID/trace → TLS/auth → RBAC → rate limit
       → schema validation → idempotency → route handler
       → Control client/circuit breaker → response/stream → audit
```

Authentication failures terminate before quota-sensitive backend work. Rate limits are principal/tenant scoped with IP fallback. Fastify JSON Schema validation removes ambiguity at the edge. Mutating routes require an idempotency key; the handler hashes canonical input, reserves the key atomically in Redis, then caches the accepted response.

## Control client

The gRPC abstraction owns channel creation, generated stubs, deadlines, metadata propagation, status translation, retry classification, and health. Route code never constructs raw RPCs. A circuit breaker opens on a rolling threshold of transport/unavailable failures, returns a retryable `503`, probes half-open with bounded concurrency, and closes after successful probes. Invalid arguments, permission denials, and business failures do not count as backend-health failures.

## Streaming

SSE is preferred for task progress; WebSocket supports interactive bidirectional sessions. A stream adapter validates task authorization, subscribes to a tenant/task partition, maps internal envelopes to public events, supports resume tokens, emits heartbeats, and applies bounded buffers. Slow consumers are disconnected with a resumable cursor rather than allowing unbounded memory. WebSocket messages are individually schema-validated and quota-accounted.

## Redis patterns

- `rate:{tenant}:{principal}:{route}:{window}`: atomic counters with expiry.
- `idem:{tenant}:{key}`: request digest, state, response reference, and TTL.
- `cache:{tenant}:{resource}:{version}`: short-lived read-through cache; no secrets.
- consumer-group state for public event fan-out; Control remains event owner.
- distributed locks only where atomic Redis operations cannot express the invariant; locks use owner tokens and expiries.

## Observability

The ingress span extracts or creates W3C trace context. Child spans cover auth, Redis, validation, gRPC and stream wait; gRPC metadata and event envelopes propagate trace/correlation IDs. Metrics record latency, status, rejection reason, breaker state, cache hit ratio, active streams, dropped/backpressured events, and backend RPC outcomes. Logs exclude JWTs, API keys, request signatures, prompts, and bodies by default.
