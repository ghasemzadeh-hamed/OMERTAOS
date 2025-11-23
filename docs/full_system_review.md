# Full-System Review

## 1. Vision & Scope
- **Vision:** Deliver a hybrid operating system (AION-OS) that unifies kernels, control plane, gateway, and console so enterprises can orchestrate AI agents and ML workloads consistently across bare metal, VMs, WSL, and containers.
- **Business value:** Accelerates AI agent deployment with reproducible registries, policy-aware governance, and turnkey installers while reducing operational friction and compliance risk.
- **Scope (in):** Control plane services (agent memory/routing/policy), gateway proxy and auth, Glass console dashboards, kernels/registries, installer profiles and compose/K8s overlays, agent/model/policy catalogs, hardening and observability hooks.
- **Out-of-scope:** Building new base ML models, non-AI business apps, long-term managed support beyond provided installers/profiles, formal compliance certifications beyond documented hardening.
- **Stakeholders (brief):** Sponsor sets vision/budget; Product Owner prioritizes catalog/console/policy; Engineering (control/kernels) maintains APIs and registries; Platform/DevOps manages installers, overlays, CI/CD; Security/compliance defines hardening and reviews policies; Operators/Data Scientists deploy and monitor agents via console/APIs.
- **Success criteria (examples):** Deployment success rate ≥98%, installer-to-running time ≤60 minutes (enterprise profile), P95 console refresh latency <3s, ≥90% agents with active policy bundles, support tickets ≤1 per 5 deployments.

## 2. High-Level Architecture & ERD
- **Architecture:**
  - **Kernels/Registry (Rust):** tenant-aware schedulers and registry definitions (`kernel/`, `kernel-multitenant/`).
  - **Control plane (Python `aion/`):** workers for agent memory, task routing, policy execution; DB + queue integrations.
  - **Gateway (TypeScript `gateway/`):** proxies API/auth/model traffic to control services and model backends; enforces auth headers/tenancy.
  - **Console (Next.js `console/`):** authenticated dashboards (NextAuth), catalog wizards, “My Agents,” policy editors, task telemetry with SSE/WebSockets.
  - **Installer & profiles (`core/`, `config/`, `configs/`, `docker-compose*.yml`):** renders `.env`, systemd/NSSM units, overlays for local/obs/vLLM.
  - **Registries & catalogs:** `ai_registry/REGISTRY.yaml`, `models/`, `config/agent_catalog/`, `agents/`, `policies/` keep artifacts reproducible.
  - **Security/observability:** hardening levels (`none`, `standard`, `cis-lite`), UFW/Fail2Ban/Auditd, SBOM/signing (`docs/security`, `docs/release.md`), OTel overlay (`docker-compose.obsv.yml`).
- **Integration boundaries:** Gateway exposes REST to clients and proxies to control plane; console consumes gateway APIs; kernels run workloads referenced by registry manifests; installer orchestrates services on bare metal/VM/WSL/Docker.
- **ERD (logical, core entities):**
```
Tenants (tenant_id PK) --< Users (user_id PK, tenant_id FK)
Tenants --< Agents (agent_id PK, tenant_id FK)
Agents --< Deployments (deployment_id PK, agent_id FK)
Agents --< Tasks (task_id PK, agent_id FK)
Tasks --< Runs (run_id PK, task_id FK)
Runs --< Artifacts (artifact_id PK, run_id FK)
Models (model_id PK) --< Agents (model_id FK)
Policies (policy_id PK) --< PolicyEnforcements (enforcement_id PK, agent_id FK, policy_id FK)
Tools (tool_id PK) --< AgentToolBindings (binding_id PK, agent_id FK, tool_id FK)
Events (event_id PK, agent_id FK / run_id FK) for audit and telemetry
```
- **Store types:** Relational DB for control metadata; object storage for artifacts; vector store for memory embeddings; queues for task dispatch; observability stack for logs/metrics/traces.

## 3. Core API Contract
- **Services & principal endpoints (via gateway):**
  - **Agent catalog:** `GET /api/agent-catalog`, `GET /api/agent-catalog/{id}` — discover catalog templates/recipes.
  - **Agent lifecycle:** `GET /api/agents`, `POST /api/agents`, `PATCH /api/agents/{id}`, `POST /api/agents/{id}/deploy`, `POST /api/agents/{id}/disable` — manage custom agents and deployments.
  - **LatentBox tools (feature-flagged):** sync/search endpoints sourced from `config/latentbox/tools.yaml`.
- **Example spec (`POST /api/agents`):**
  - **Method/Path:** `POST /api/agents`
  - **Request JSON:**
    ```json
    {
      "name": "my-agent",
      "model": "model://gpt-4o",
      "policy_ids": ["default-safe"],
      "tool_ids": ["search"],
      "config": {"max_tokens": 1024}
    }
    ```
  - **Response 201 JSON:**
    ```json
    {
      "id": "agt_123",
      "status": "created",
      "deployment": null
    }
    ```
  - **Status codes:** 201 created; 400 validation error; 401/403 auth or RBAC failure; 404 unknown model/policy/tool; 429 rate-limit (if enabled); 500 on server error.
  - **Errors:** JSON `{ "code": "invalid_input", "message": "model not found" }`.
- **Versioning:** `/api/v1/...`; breaking changes gated by new version with deprecation window; console tracks API version via gateway.
- **Rate limiting:** Configurable at gateway; recommend defaults (e.g., 1000 req/min per tenant, burst 200) with 429 responses.
- **Curl example:**
  ```bash
  curl -X POST https://aion.example.com/api/v1/agents \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"my-agent","model":"model://gpt-4o","policy_ids":["default-safe"],"tool_ids":["search"],"config":{"max_tokens":1024}}'
  ```

## 4. Installation & Setup
- **Developer setup:**
  - Prereqs: Git, Docker Engine/Compose, Python 3.11+, Node 18+, OpenSSL; on Windows use WSL2 + Docker Desktop.
  - Steps: `git clone ... && cd OMERTAOS`; copy `dev.env` to `.env`; run `./quick-install.sh` (or `./quick-install.ps1` on Windows) to generate dev certs/JWT keys and start compose stack with developer overlay; or `./install.sh --profile user --local`.
  - Verification: `docker compose ps` shows gateway/control/console up; hit console UI or `curl /api/health` via gateway.
- **Production setup:**
  - Prereqs: Ubuntu host/VM or Kubernetes cluster; root/sudo access; outbound internet for package fetch unless using cached ISO; optional GPU drivers for vLLM overlay.
  - Steps: choose profile (`user|pro|enterprise`); run `./install.sh --profile enterprise` (Linux) or `./install.ps1 -Profile enterprise` (Windows/WSL) to render `.env`, systemd/NSSM units, compose overlays; for quick compose-only, use `docker compose -f docker-compose.yml -f docker-compose.obsv.yml up -d` or `-f docker-compose.vllm.yml` as needed.
  - Configuration: profiles under `config/profiles`; env templates in `config/templates/.env.example`; adjust `config/agent_catalog` and `ai_registry` as needed.
  - Verification: `systemctl status aion-*` (Linux) or `Get-Service aion-*` (Windows); console login; `GET /api/agents` returns 200.

## 5. Runbook + Backup Strategy
- **Daily operations (SOP):**
  - Start: `docker compose up -d` (or `systemctl start aion-*`); verify health endpoints and console login.
  - Stop: `docker compose down` (or `systemctl stop aion-*`).
  - Health: check `/api/health`, console dashboards, and logs in central aggregator; watch queue depths and database connections.
  - Rollback (app): redeploy previous image tag via compose/k8s; if migrations shipped, apply rollback script or restore pre-release DB snapshot.
- **Backup strategy:**
  - Scope: relational DB, object store bucket for artifacts, vector store indices, configuration (`.env`, registry/manifests), and logs.
  - Cadence: daily full + hourly incremental for DB; daily snapshot of object store; weekly archive of logs/configs.
  - Location: primary storage plus off-site/cloud replica; encryption at rest; retention 30–90 days (per policy).
  - Verification: weekly restore test in staging; checksum validation for artifacts; alert on failed jobs.

## 6. Security (Deep)
- **AuthN/Z:** Gateway uses bearer tokens (NextAuth/OAuth2/JWT); console supports credential + Google OAuth; RBAC by tenant with role-scoped APIs; service-to-service via signed headers/keys.
- **Data security:** TLS in transit (reverse proxy certs, dev self-signed generated by quick-install); encryption at rest via disk/FDE and encrypted buckets; secrets managed via environment files or Vault/KMS; rotate keys on schedule or on compromise.
- **Threat model (sample):**
  | Asset | Threat | Control |
  | --- | --- | --- |
  | Gateway APIs | Credential theft, brute force, SSRF | OAuth2/NextAuth, rate limiting, WAF/allowlist, mTLS to backends |
  | Control DB | Unauthorized access, exfiltration | Network isolation, RBAC, encryption at rest, audit logging, least-privileged creds |
  | Artifacts/object store | Tampering, leakage | Signed uploads, bucket policies, integrity checksums, retention + versioning |
  | Console sessions | CSRF/XSS, session hijack | SameSite/HttpOnly cookies, CSP, CSRF tokens, MFA for admins |
  | Model/registry manifests | Supply-chain poisoning | SBOM, signing, checksum verification in CI/release |
- **Vulnerability management:**
  - Dependency scanning in CI; weekly CVE review; critical CVEs patched within 48 hours; medium within 14 days.
  - Emergency patch flow: branch -> targeted tests -> staged rollout -> monitor -> finalize; rollback via previous image and config pinning.
- **Network security:**
  - Segmentation: public LB -> gateway in DMZ/VPC front tier; control DB/queues/object store in private subnets; console behind gateway auth.
  - Firewalls/SGs: allow 80/443 inbound to gateway; restrict DB/queue/OTel ports to app subnets; egress allowlist as needed; VPN/SSH bastion for admin access.

## 7. Observability
- **Monitoring:** latency (P95), error rate, throughput, queue depth, DB connections, CPU/RAM/GPU, disk, SSE/WebSocket health; use Prometheus/Grafana or Datadog; OTel collector via `docker-compose.obsv.yml`.
- **Logging:** structured JSON with timestamp, level, service, correlation/trace ID, request ID, tenant, user; centralized aggregation (ELK/Datadog); retention aligned to policy (e.g., 30–90 days); debug logs off in prod.
- **Alerts:** 5xx error rate >0.1% over 5m; latency P95 >3s; queue lag > threshold; DB CPU >80% for 10m; disk <15% free; TLS expiry <14 days. Escalate Sev1 to on-call within 5m.
- **Tracing:** OpenTelemetry SDK/collector; propagate traceparent headers through gateway/control; console front-end includes trace IDs; use traces for root-cause in latency spikes.
- **Dashboards:** service uptime, agent deployment success, task/run throughput, policy enforcement counts, resource utilization; owners per team (control, platform, console); weekly review.

## 8. Disaster Recovery (DR) & Resilience
- **Objectives:** Critical services RTO ≤4h, RPO ≤1h (DB/object store); console/gateway RTO ≤2h with warm standby; artifacts RPO 24h unless stricter policy required.
- **Scenarios & actions:**
  - **Primary DC/region down:** Detect via health checks; fail over DNS/LB to standby region; promote replica DB; point object store to replicated bucket; validate APIs/console; backfill missed queue events.
  - **Ransomware/data corruption:** Isolate hosts; rotate creds; restore DB/object store from last clean snapshot; run integrity checks; re-enable services after verification.
  - **Gateway/service outage:** Roll back to previous image; drain/redirect traffic; verify health and latency before full cutover.
- **High availability:** Multi-AZ or multi-region gateway nodes; DB with replicas; queues with durability; stateless services scaled horizontally; readiness/liveness probes with rolling deploys/canaries.
- **Data lifecycle & retention:** Operational data retained per profile (30–90 days for logs, longer for audit if required); archive artifacts to cold storage after 90 days; delete per policy and regulatory needs (e.g., GDPR erasure on request).
- **DR testing:** Semi-annual failover drills; quarterly backup restore tests; success criteria include RTO/RPO met, data integrity verified, and alerting/reporting captured; DR owner: platform/SRE lead.
