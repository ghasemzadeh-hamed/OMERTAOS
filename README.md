# OMERTAOS Architecture Blueprint

This repository captures the reference architecture for OMERTAOS, focusing on
secure, policy-driven AI task orchestration across heterogeneous execution
environments. The material is organised so that you can quickly identify
responsibilities, data flows, and operational guidance when evolving the
platform.

## Documentation Map

| Area | Description |
| --- | --- |
| [`docs/architecture.md`](docs/architecture.md) | Canonical blueprint covering control, data, security, and runbook details. |
| [`LICENSE`](LICENSE) | Licensing information for the documentation set. |

## Quick Highlights

* **Execution Model** – WASM-first with hardened subprocess fallback to balance
  portability and hardware access.
* **Control Plane** – FastAPI decision router orchestrating policies, intents,
  and provider selection via Kafka-backed eventing.
* **Data Fabric** – Postgres, Mongo, Kafka, Qdrant, and MinIO provide
  structured, unstructured, vector, and object storage foundations.
* **Observability & Security** – OTEL tracing, Prometheus metrics, Cosign/SBOM
  validation, and RBAC/ABAC enforcement ensure operational clarity and supply
  chain integrity.

Refer to the detailed blueprint for comprehensive sequences, policies, and
operational runbooks.
