# SEAL-Style Memory Execution Plan for OMERTAOS / AION-OS

## Objective
Implement a production-grade SEAL-inspired continuous self-adaptation loop for OMERTAOS that captures self-edits, trains lightweight adapters, and safely routes agents to the best performing model variants.

## High-Level Workstreams
1. **Memory Service (`aion-memory`)** – persistent capture of interactions and self-edits with governance controls.
2. **SEAL Adapter Service (`aion-seal-adapter`)** – automated data curation, lightweight fine-tuning, evaluation, and promotion workflows.
3. **Model Registry & Router (`aion-model-registry`)** – centralized catalog of model variants, metadata, and routing policies.
4. **Platform Integration** – connect the new services with the existing OMERTAOS gateway, control plane, observability stack, and deployment tooling.

Each workstream below includes milestones, deliverables, and dependencies so the team can start implementation immediately.

## 1. `aion-memory` Service
### Scope
Create a dedicated microservice responsible for storing raw interactions, self-edits, and evaluation artifacts. Provide APIs for querying and exporting training-ready datasets.

### Deliverables
- **Data Model & Storage**
  - Choose PostgreSQL (preferred for transactions + JSONB flexibility). Provision new schema `aion_memory`.
  - Tables:
    - `interactions`: columns for `id (UUID)`, `agent_id`, `tenant_id`, `user_id`, `input_text`, `output_text`, `model_version`, `channel`, `timestamp`, `metadata JSONB`.
    - `self_edits`: `id`, `interaction_id (FK)`, `editor_type` (`human`, `model`, `rule`), `original_output`, `edited_output`, `reason_code`, `reward_score`, `timestamp`, `metadata JSONB`.
    - `evaluations`: `id`, `model_version`, `dataset_id`, `metric_name`, `metric_value`, `run_id`, `timestamp`, `metadata`.
  - Indexing on `agent_id`, `tenant_id`, `timestamp` for efficient slicing.

- **API** (FastAPI)
  - `POST /interactions` – ingest interaction payloads from gateway/control.
  - `POST /self-edits` – ingest approved edits (requires reference to interaction).
  - `GET /datasets/sft` – export curated SFT datasets filtered by reward/tenant/agent.
  - `GET /interactions/{id}` – retrieve single interaction for audit.
  - `GET /healthz` – service health endpoint.
  - Auth via existing OMERTAOS service mesh JWT with tenant scoping middleware.

- **Ingestion Workers**
  - Background task to enforce retention policies (archive old interactions to MinIO after N days).
  - Optional Kafka consumer for streaming ingestion if needed by high-traffic agents.

- **Observability**
  - OTEL tracing integration.
  - Prometheus metrics: request latency, dataset export counts, edit approval rate.

### Milestones
1. Schema migration files + Alembic integration (Day 1).
2. API skeleton with auth middleware and OpenAPI docs (Day 2–3).
3. Integration tests using pytest + Testcontainers (Day 4).
4. Deployment manifest (Helm chart + docker-compose override) (Day 5).

## 2. `aion-seal-adapter` Service
### Scope
Automate the SEAL loop: curate high-quality self-edits, fine-tune adapters, evaluate, and publish candidate models.

### Deliverables
- **Data Pipeline**
  - Scheduled job (Celery beat / APScheduler) that fetches top-N edits via `aion-memory` API.
  - Filtering heuristics: minimum reward threshold, deduplicate by `interaction_id`, enforce tenant/domain grouping.
  - Dataset assembler outputs JSONL with `prompt`, `response`, `metadata`.

- **Training Module**
  - Use PEFT + LoRA on selected base checkpoints (e.g., `aion-base`, `aion-base-sales`).
  - Configurable hyperparameters per tenant/domain stored in config YAML.
  - Training orchestrated via HuggingFace `Trainer` with DeepSpeed stage 2 if GPUs available; fallback to CPU-friendly quantized adapters.
  - Store resulting adapter weights in MinIO bucket `seal-adapters/{model_name}/{timestamp}`.

- **Evaluation Suite**
  - Run regression suite using existing `tests/llm_evals` (create if absent):
    - Automatic metrics (BLEU, Rouge, factuality classifier).
    - Scenario-based prompts curated per tenant.
  - Summarize metrics into structured report persisted via `aion-memory` `evaluations` table.

- **Promotion Logic**
  - Compare candidate metrics vs baseline using configurable thresholds.
  - On success, call `aion-model-registry` `POST /models` to register new version with metadata (parent ID, adapters location, metrics snapshot).
  - On failure, log reasons and push alerts to Grafana via Alertmanager webhook.

- **Operational Concerns**
  - Container image with CUDA runtime + requirements (PEFT, bitsandbytes, accelerate).
  - Support dry-run mode for staging.
  - Feature flag to disable auto-promotion, requiring manual approval through registry UI.

### Milestones
1. Dataset builder + scheduler (Day 1–2).
2. Training pipeline with mock model (Day 3–5).
3. Evaluation harness wired to metrics store (Day 6–7).
4. Promotion + alerting flows (Day 8).
5. End-to-end dry run in staging (Day 9).

## 3. `aion-model-registry` Service
### Scope
Provide a central catalog for model versions, lineage, routing rules, and deployment configuration consumed by the gateway/control plane.

### Deliverables
- **Data Model (PostgreSQL schema `aion_registry`)**
  - `models`: `id`, `name`, `parent_id`, `adapter_uri`, `status`, `created_at`, `created_by`, `description`.
  - `metrics`: `id`, `model_id`, `metric_name`, `metric_value`, `dataset_id`, `timestamp`.
  - `routes`: `id`, `agent_id`, `tenant_id`, `default_model_id`, `fallback_model_id`, `policy_json`.
  - `deployments`: `id`, `model_id`, `environment`, `replica_count`, `autoscale_policy`, `config_json`.

- **API** (FastAPI or Node.js)
  - `GET /models`, `GET /models/{id}`, `POST /models` (with validation + RBAC).
  - `POST /routes` & `GET /routes/{agent_id}` for agent orchestrator integration.
  - `POST /evaluations/import` to ingest evaluation summaries from `aion-seal-adapter`.
  - Auth & audit logging integrated with OMERTAOS IAM.

- **Admin UI (Phase 2 optional)**
  - Simple React dashboard embedded in existing console to inspect models, metrics, and routing policies.

- **Integration Hooks**
  - gRPC/REST client library for gateway/control services to resolve routing decisions at runtime.
  - Webhook emitter for deployment triggers (e.g., notify Kubernetes operator to roll out new adapter).

### Milestones
1. Schema migration + API skeleton (Day 1–3).
2. Route resolution SDK for Python services (Day 4–5).
3. Integration tests + contract tests with gateway (Day 6–7).
4. Optional UI stub + documentation (Day 8–9).

## 4. Platform Integration
### Tasks
- **Gateway / Control Plane Updates**
  - Inject middleware to log every agent interaction to `aion-memory`.
  - Replace static model config with dynamic lookup via registry client.
  - Implement fallback strategy: if registry unavailable, use cached model assignments.

- **CI/CD**
  - Extend existing GitHub Actions (or GitLab CI) to build/push images for new services.
  - Add integration tests triggered nightly running SEAL loop in staging.
  - Define versioning scheme (e.g., semantic + timestamp `aion-base+seal-sales@2025.04.01`).

- **Observability & Governance**
  - Dashboards combining interaction volume, edit acceptance, training cadence, model quality trends.
  - Audit logs linking each model version to source edits and evaluation results.
  - Runbooks for rollback: how to deactivate problematic adapters, revert routes, purge edits.

- **Security**
  - Ensure data isolation per tenant via row-level security policies in PostgreSQL.
  - Encrypt adapter artifacts at rest in MinIO with KMS-managed keys.
  - Implement PII scrubbing pipeline for interaction logs before dataset export.

## Implementation Timeline (Two-Week Sprint Example)
| Day | Workstream | Key Outcomes |
| --- | ---------- | ------------ |
| 1 | Memory | DB schema, migrations scaffold |
| 2 | Memory | REST API endpoints drafted |
| 3 | Memory | Auth + integration tests |
| 4 | Adapter | Dataset builder, scheduler |
| 5 | Adapter | Training loop prototype |
| 6 | Adapter | Evaluation harness wired |
| 7 | Registry | Schema + API skeleton |
| 8 | Registry | Routing SDK + tests |
| 9 | Adapter | Promotion flow, staging run |
| 10 | Platform | Gateway logging integration |
| 11 | Platform | Registry routing integration |
| 12 | Platform | CI/CD pipeline updates |
| 13 | Platform | Observability dashboards |
| 14 | Platform | Final QA, rollback drills |

## Next Steps for Tomorrow
1. Spin up local docker-compose stack with PostgreSQL and MinIO dedicated to SEAL services.
2. Generate Alembic migrations for `aion-memory` and `aion-model-registry` schemas.
3. Scaffold FastAPI projects with shared auth middleware (`shared/auth/jwt.py`).
4. Define pydantic models for interaction/self-edit payloads under `schemas/aion_memory/`.
5. Draft scheduler script in `tools/seal_adapter/runner.py` invoking placeholder training routine.
6. Prepare CI workflow file `./.github/workflows/seal-services.yml` building and testing the three services.

## Dependencies & Risks
- **GPU Availability** – ensure staging environment has access to GPU nodes for LoRA training; otherwise rely on CPU quantization and accept longer cycles.
- **Data Quality** – need manual review pipeline or reward model to prevent bad self-edits contaminating training data.
- **Regulatory** – confirm retention policy compliance before logging customer data; integrate redaction filters early.
- **Change Management** – communicate with customer success teams about adaptive behavior and provide opt-out controls per tenant.

## Success Metrics
- Time from self-edit approval to promoted model < 24 hours.
- >5% improvement in relevant evaluation metrics per domain within first month.
- Zero Sev-1 incidents linked to automated promotions (rollback mean time < 10 minutes).
- Full audit trace available for every promoted model (source edits + evaluation report).

---
This plan gives the engineering team a concrete, sequenced backlog to begin building SEAL-style memory inside OMERTAOS immediately.
