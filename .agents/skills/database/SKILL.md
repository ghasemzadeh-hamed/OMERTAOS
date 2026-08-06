---
name: database
description: Analyze or implement OMERTAOS schema, migration, seed, adapter, index, and data-integrity work. Use only for database-focused tasks, not generic data access.
---

# OMERTAOS Database Skill

## Execution Mode

- For implementation requests, patch the existing data architecture and add
  targeted migration/data tests; do not stop at a schema proposal.
- For analysis-only requests, remain read-only.
- Documentation is required only for an actual migration, setup change, or
  operator-visible database workflow.

## Data Sources

- Postgres
- Redis
- MongoDB
- Qdrant
- MinIO
- SQLite adapters for local/dev where present

## Rules

- Never drop, truncate, overwrite, or delete data without explicit approval.
- Prefer backward-compatible, idempotent migrations and repeatable seeds.
- Check for existing objects before creation and preserve records.
- Avoid raw dynamic SQL and use safe bindings.
- Add indexes only with evidence and a reason.
- Preserve tenant isolation and permission-aware retrieval.
- Treat `data/` as canonical; compatibility roots remain until their retirement
  gates pass.
