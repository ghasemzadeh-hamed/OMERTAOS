# ADR 0003: Public gRPC Endpoint

## Context

Clients demand low-latency streaming and typed contracts.

## Decision

Expose a public gRPC API (`aion.v1.AionTasks`) alongside REST. Use mutual TLS and JWT metadata in production.

## Consequences

- Requires generated stubs for multiple languages.
- Gateway must maintain gRPC client and propagate trace context.
