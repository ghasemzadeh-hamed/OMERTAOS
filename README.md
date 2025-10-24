# OMERTAOS Architecture Overview

OMERTAOS is an AI orchestration platform designed around strong tenancy, 
policy-driven routing, and WASM-first module execution. This repository captures
the high-level architecture, operational strategy, and reference manifests.

## Documentation Index

| Document | Description |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | Comprehensive logical architecture, runtime model, data stores, and operational practices. |
| [docs/runbook.md](docs/runbook.md) | Day-2 operations, monitoring, incident response, and release workflows. |
| [docs/reference-manifests.md](docs/reference-manifests.md) | Sample YAML manifests for intents, policies, models, modules, and AIP packages. |

All documents are structured to support single-tenant initial deployments with a
clear migration path to multi-tenant without disruptive schema changes.
