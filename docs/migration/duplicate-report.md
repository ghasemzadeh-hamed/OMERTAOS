# Duplicate report — Structure S0

Date: 2026-07-12

Method: exact Git blob identity at `HEAD`, followed by ownership grouping.

Exact identity proves equal content at this commit, not that either copy is safe
to delete. Empty package markers and intentionally repeated examples are listed
separately from ownership conflicts.

## Canonical versus legacy duplicates

| Area | Confirmed examples | Intended owner | S0 decision |
|---|---|---|---|
| Runtime | `runtime-daemon/src/sandbox/process.rs` = `rust-runtime/sandbox/process.rs`; matching mount, signature, server and cluster files also exist | `runtime-daemon/` | `MERGE`; compare Cargo modules and callers in S2 |
| Data/RAG | `data/rag/retriever.py` = `database/retriever.py`; reranker also matches | `data/` | `MERGE` in S3 after import tests |
| Models | matching YAML profiles exist under `models/` and `registry/models/` (including Google, DeepSeek, Meta, Moonshot and custom) | `registry/models/` | `MERGE`; verify the complete set and consumers |
| Deployment | identical systemd, scripts, bundles, CI and observability assets occur under `deploy/` and `execution/` | `deploy/` | `MERGE` in S4; preserve Quickstart/Native parity |
| Windows Bridge | multiple exact source, manifest, config and documentation copies under `execution/windows-agentic-bridge/` and `integrations/windows-agentic-bridge/` | `integrations/windows-agentic-bridge/` | `MERGE`; diff entire trees before reference updates |
| Schemas | `schemas/events/audit_activity.schema.json` = `schemas/v1/events/audit_activity.schema.json` | `schemas/v1/` | `MERGE`; validate schema consumers/versioning |
| Observability | `observability/bus.py` = `shared/event_bus/bus.py` | Split between `shared/` and `integrations/` | `SPLIT`; architecture decision required |

## Repeated content requiring no immediate cleanup

- Six empty adapter `__init__.py` files under `db/adapters/` share one blob.
- Empty package markers across unrelated packages share blobs by design.
- Example `VERSION`, router policy and data-source files repeat within bundle
  templates; their packaging semantics must be tested before deduplication.
- Four placeholder Rust `mod.rs` files share content; module ownership, not hash,
  determines whether they remain.

## Required comparison protocol

Before any merge or deletion:

1. Review `git log --oneline -- <legacy> <canonical>`.
2. Run a full directory/file diff, including unique and newer files.
3. Map imports, build inputs, deployment references and tests.
4. Migrate references and run the phase-specific acceptance suite.
5. Delete only in S5 after the canonical copy is proven authoritative.
