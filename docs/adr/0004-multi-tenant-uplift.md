# ADR 0004: Multi-Tenant Ready Design

## Context

Initial release targets single tenant but must scale to multi-tenant deployments.

## Decision

Reserve `tenant_id` fields in schemas, add tenant-aware Redis keys, and namespace Qdrant collections. Policies allow per-tenant overrides.

## Consequences

- Database migrations need to include tenant columns.
- Access control requires tenant scoping for API keys and JWT claims.
