# Infrastructure & DevOps Review

## 1. Infrastructure Diagram
- **Deployment model:** Hybrid-friendly - supports on-premises (bare metal/VM) and cloud (Kubernetes/managed DB/object storage) with identical compose overlays.
- **Textual diagram (suitable for drawing):**
  - Box: *Users/Operators* (Browser/CLI) -> arrow to *Edge Load Balancer* (HTTPS, WAF/Rate limit).
  - Edge Load Balancer -> arrow to *Gateway Service* (ingress controllers / API gateway) inside *Public/DMZ subnet*.
  - Gateway -> arrow to *Control Plane* namespace in *Private subnet* (Kubernetes cluster or VM pool) hosting Control, Kernel Scheduler, Policy Engine, Memory/Task workers.
  - Control Plane -> bidirectional arrows to *Data Plane*: Postgres (primary + read replica), Redis, Qdrant (vector), MinIO/S3 (artifacts), Kafka (events), and OTEL/Prometheus collectors (observability).
  - *Bastion/Jump host* in management subnet -> access to cluster nodes and databases over VPN/privileged network.
  - External dependencies: IdP (OIDC/SAML), Secret Manager (Vault/KMS), OCI/ORAS Registry, External LLM APIs; shown as boxes with arrows into Gateway/Control.
  - Multi-AZ recommended: duplicate compute and data plane nodes across at least two zones; object storage bucket is cross-AZ/region replicated.

## 2. Environments (Dev, Test, Staging, Prod)
- **Dev:** Local Docker Compose or single-node k3d/k3s; seeded sample data; permissive RBAC; feature flags enabled for rapid iteration; minimal autoscaling.
- **Test/CI:** Ephemeral namespaces spun per pipeline; realistic secrets via CI vault; executes unit/integration suites and contract tests; synthetic data only.
- **Staging/Pre-Prod:** Mirrors production topology (multi-AZ cluster, managed DBs) with smaller instance sizes; connected to staging IdP; runs load/regression tests before promotion; blue/green or canary rehearsals occur here.
- **Production:** Hardened RBAC, network policies enforced, HPA/cluster autoscaler enabled, auditing on; observability SLO alerts active; only masked production-like data where mandated.
- **Promotion path:** Feature branch -> PR -> CI (unit/integration/linters) -> deploy to Test namespace -> automated smoke -> promote tag to Staging -> canary/blue-green -> Production upon approval and health checks.

## 3. Compute & Container/VM Setup
- **Container runtime:** Containerd; images built via Docker/BuildKit with SBOM/signing.
- **Kubernetes architecture:**
  - Namespaces: `gateway`, `control`, `schedulers`, `data`, `obsv`, `ci-preview` (ephemeral), `admin`.
  - Node pools: general-purpose for Gateway/Control; CPU-optimized for Kafka/Redis; memory-optimized for Postgres; optional GPU/AVX nodes for model execution.
  - Ingress: NGINX/Envoy ingress controllers with TLS termination; service mesh (Istio/Linkerd) optional for mTLS and traffic shifting.
  - Autoscaling: HPA on Gateway/Control/Workers; Cluster Autoscaler tied to node pools; PDBs and Pod anti-affinity for AZ spread.
- **VM/bare metal (on-prem):**
  - Minimum 3 control-plane nodes, 3+ worker nodes; dedicated storage nodes for MinIO and Postgres with RAID/ZFS; HAProxy/Keepalived for VIP load balancer.
- **Container scheduling:** Runtimes pinned to namespaces; tolerations/taints used to isolate GPU tasks; CronJobs for cleanup/retention jobs.

## 4. CI/CD Pipeline
- **Source control:** Trunk-based with short-lived feature branches; `main` protected with required reviews and status checks.
- **Build:** Trigger on PR and main merges; lint (ruff/eslint), type-check (pyright/tsc), unit tests; build multi-arch images with provenance attestation; publish to internal registry with semantic tags.
- **Testing gates:**
  - Unit + contract tests in CI namespace using mocked/externalized secrets.
  - Integration/e2e flows against ephemeral environment; load tests run nightly against Staging with synthetic datasets.
  - Security: SAST (semgrep), dependency scanning, container image scan (Trivy/Grype), IaC scan (tfsec) as mandatory gates.
- **Deploy strategy:**
  - Staging: rolling or blue/green via Argo CD/Flux with health checks.
  - Production: canary (e.g., 10/30/100) with automatic rollback on SLO breach; database migrations run in pre-deploy job with fallback plans.
- **Feedback/observability:** CI publishes test artifacts and coverage; deployment pipeline emits events to Slack/Teams; post-deploy smoke tests and synthetic probes validate endpoints.

## 5. Secrets Management & Configuration
- **Secret store:** Vault or cloud KMS/Secrets Manager; sealed-secrets or CSI driver for Kubernetes; `.env` only for local dev.
- **Rotation:** Short-lived tokens (OIDC/JWT), database credentials rotated via dynamic secrets/TTL; key rotation quarterly or on incident.
- **Injection:** Workloads consume secrets via projected volumes or env vars with least-privilege service accounts; external secret operators sync to namespaces.
- **Configuration policy:** ConfigMaps for non-sensitive settings; per-environment overlays (Helm/Kustomize) keep drift minimal; forbidden to hardcode credentials.

## 6. Network Topology & Security
- **VPC/Segmentation:** Three subnets per AZ (public for ingress, private for app, isolated for data). Network policies restrict east-west; service mesh enforces mTLS.
- **Ingress:** HTTPS only via WAF+ALB/NLB; TLS 1.2+; HSTS and rate limiting enabled. WebSockets/SSE allowed through Gateway paths.
- **Egress:** NAT gateways for outbound; egress policies whitelist external LLM/registry endpoints; no direct internet from data subnet.
- **Firewalls/Security Groups:** Principle of least privilege; DB ports limited to app subnets; Kafka/Redis not exposed publicly; bastion via VPN/JIT access.
- **Monitoring & logging:** Flow logs, WAF logs, ingress/egress metrics shipped to SIEM; DDoS protection enabled where available.

## 7. Resource Sizing & Capacity Planning
| Layer | Baseline Size | Notes/Scaling | Metrics for Planning |
| --- | --- | --- | --- |
| Gateway | 2-3 pods (0.5-1 vCPU, 1-2 GiB) per AZ | HPA on CPU/RPS/latency; canary friendly | P95 latency, error rate, RPS |
| Control | 3-5 pods (1-2 vCPU, 2-4 GiB) | Scales on queue depth/task throughput | Queue depth, task success rate |
| Kernel/Schedulers | 2-N pods (2-4 vCPU, 4-8 GiB; GPU optional) | Autoscale on job concurrency and GPU utilization | Concurrency, GPU/CPU utilization |
| Postgres | 2 nodes (primary + read replica, 4-8 vCPU, 16-32 GiB, fast SSD) | Vertical scale for IOPS; follower for reads | TPS, buffer hit ratio, IOPS |
| Redis | 3-node cluster (cache) | Scale memory; enable clustering if >50GB | Evictions, latency, hit rate |
| Qdrant | 3 nodes (CPU+RAM heavy) | Scale shards on vector count; pin to NVMe | Recall/latency, shard balance |
| MinIO/S3 | 4+ nodes or managed bucket | Erasure coding; autoscale frontends | Storage growth, egress, 4xx/5xx |
| Kafka | 3-5 brokers (2-4 vCPU, 8-16 GiB) | Scale partitions; dedicate disks | Lag, throughput, ISR count |
- **Growth model:** Start with above baseline for ~1k RPS and tens of concurrent jobs; increase nodes 2x for each additional 1k RPS or 2x vector/object growth. Use autoscaling policies tied to SLOs and cost budgets.

## 8. Additional Considerations
- **IaC:** Terraform/Helm/Kustomize as source of truth; GitOps (Argo CD/Flux) for drift detection and pull-based deploys.
- **DR/BCP:** Multi-AZ default; optional cross-region standby with async DB replication and replicated object storage; quarterly failover drills; RPO <= 15 minutes (db), RTO <= 2 hours for control plane.
- **Compliance:** Encrypt data in transit (mTLS/TLS 1.2+) and at rest (KMS-managed keys); audit logging retained per policy; align with SOC2/ISO27001 controls where applicable.
- **Gaps/Recommendations:**
  - Add formal canary policy for all services and automatic rollback hooks.
  - Implement periodic secret rotation jobs and validate mTLS between all services.
  - Ensure capacity tests include GPU nodes and vector workloads; document burst limits for external LLM calls.
