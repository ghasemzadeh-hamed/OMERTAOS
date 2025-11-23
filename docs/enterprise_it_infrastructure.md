# Enterprise IT & Infrastructure Review

## 1. Asset Inventory
- Maintain a CMDB-backed inventory with lifecycle states (planned, active, maintenance, standby, decommissioned) and ownership mapped to platform, network, or security teams.
- Representative assets:
  - **Compute/Containers**
    - `srv-core-01` / `srv-core-02`: VM hosts (Ubuntu LTS, KVM), private IPs `10.10.10.21-22`, host AION control plane and gateway; owners: Platform; status: active; location: primary DC rack R1.
    - `k8s-mgmt-01..03`: Kubernetes control-plane nodes (v1.28), private IPs `10.10.20.10-12`; owners: Platform; status: active; location: primary DC; lifecycle: 36-month refresh.
    - `k8s-gpu-01..04`: Worker nodes with NVIDIA A100 GPUs, private IPs `10.10.20.30-33`; owners: Platform; status: active; location: primary DC; lifecycle: 24-month refresh.
  - **Network**
    - `fw-edge-01`: Next-gen firewall; public IP `203.0.113.10`, private transit `10.10.0.1`; owners: Network; status: active; location: perimeter/DMZ.
    - `lb-ext-01`: L4/L7 load balancer for console/gateway; VIP `203.0.113.20`; backend pool `10.10.10.21-22` and `10.10.20.30-33`.
    - `vpn-hub-01`: IPSec/SSL VPN terminator; public IP `203.0.113.30`; owners: Network; status: active; MFA enforced for remote access.
  - **Data**
    - `db-core-01`: PostgreSQL 15 HA pair (Patroni); private IPs `10.10.30.10-11`; owners: Data; status: active; encrypted disks; lifecycle: 36-month refresh.
    - `s3-obj-01`: Object store (MinIO/S3 compatible); endpoint `s3.internal`, private `10.10.40.10`; owners: Platform; status: active; versioning enabled.
    - `vec-01`: Vector DB service (pgvector/Weaviate); private `10.10.30.20`; status: active; owners: Data; lifecycle: 24-month refresh.
  - **Services**
    - AION control plane (`aion`, `gateway`, `kernel`): runs in Kubernetes `aion-system` namespace; version pinned per release tags; owners: Platform.
    - Observability stack (Prometheus/Grafana/Loki/Tempo): namespace `obsv`; owners: SRE; status: active.
- Tag all assets with business service, cost center, owner, environment, and patch group; align with ITAM by enforcing intake forms, periodic recertification, and disposal logs.

## 2. Network Diagram
Textual view suitable for diagramming:
- **Zones**
  - Office LAN (`10.20.0.0/16`): user workstations; outbound to VPN hub only; no inbound from DC/VPC.
  - Remote-access VPN: terminates on `vpn-hub-01`; allows least-privileged access to Jump/Bastion and select services.
  - DMZ: `fw-edge-01` fronting `lb-ext-01`; exposes HTTPS 443 to public for console/gateway; SSH blocked.
  - Data-centre core (`10.10.0.0/16`): Kubernetes cluster nodes, databases, object store; east-west allowed only via security groups.
  - Observability enclave: `obsv` subnet `10.10.50.0/24`; inbound from cluster via scrape targets; egress restricted.
- **Rules (summary)**
  - Internet &#x2192; DMZ: allow 443/TCP to `lb-ext-01`; deny all else.
  - DMZ &#x2192; Core: `lb-ext-01` to gateway/control plane on 80/443 (mTLS preferred); health checks to nodes on 10250/metrics via allowlist.
  - VPN &#x2192; Bastion: allow SSH/RDP only to jump host; onward access via RBAC and short-lived certificates.
  - Core &#x2192; Data: app namespaces to PostgreSQL 5432, Vector DB 5433/HTTPS, Object store 9000/HTTPS; deny lateral pod-to-pod across namespaces unless labeled.
  - Observability: scrape 9090/4317/4318 from obsv to workloads; logs/metrics egress only to storage endpoints; no ingress from internet.
- **Critical paths**: Internet &#x2192; LB &#x2192; Gateway/Console; Gateway &#x2192; Control plane APIs; Control plane &#x2192; DB/Vector/Object; Cluster &#x2192; Observability stack; VPN &#x2192; Bastion &#x2192; Admin paths.

## 3. Standard Operating Procedures (SOP)
- **User creation/deletion**
  - Prereqs: approved ticket, manager + security sign-off; existing MFA enrollment.
  - Steps: create identity in IdP with least-privilege group; provision VPN + console SSO; tag owner/cost center; verify login; log change ticket.
  - Deletion: disable account, rotate service tokens, remove from groups, revoke VPN, archive home directories; verify by attempted login failure; record completion.
  - SLA: acknowledge within 4h business; complete within 1 business day.
- **Password reset**
  - Request via service desk; verify identity (MFA push + manager confirmation for privileged roles); reset in IdP; force next-login rotation; log in audit trail; SLA: 2h.
- **Access request**
  - Workflow: request &#x2192; manager approval &#x2192; data owner approval (for PII) &#x2192; provisioning via roles/policies &#x2192; confirmation; enforce least-privilege RBAC; review monthly.
- **VM/resource request**
  - Form includes environment, sizing (vCPU/RAM/GPU), storage class, network zone, cost center, retention window.
  - Approvals: platform lead + cost center owner; enforce tagging (service, env, owner, expiry).
  - Provision via Terraform/Ansible; baseline hardening + agent install; verify monitoring/backup enrollment; decommission via ticket with data wipe and CMDB update.

## 4. Backup & Disaster Recovery Plan (DR)
- **Objectives**: Critical control-plane data RPO &#x2264; 30 minutes (WAL shipping); RTO &#x2264; 4 hours; object store RPO &#x2264; 4 hours; observability RPO &#x2264; 24 hours.
- **Backups**
  - PostgreSQL: nightly full, 15-minute WAL archiving to off-site object storage; retention 30 days; weekly integrity restore test in staging.
  - Object store: versioning + daily incremental to secondary region; retention 60 days; quarterly restore drill.
  - Kubernetes state: etcd snapshots daily; manifests stored in Git; Velero backups for namespaces (aion-system, obsv) nightly; retention 14 days.
- **DR scenarios**
  - DC outage: fail over to warm standby region; bring up Kubernetes from IaC; restore DB from latest WAL; repoint DNS/LB; verify gateway/console health.
  - Ransomware: isolate network, rotate credentials, restore from clean backups, validate hashes/SBOM; re-enable services after regression checks.
  - Major outage: invoke incident bridge, promote standby DB, scale worker nodes, validate observability; publish comms templates.
- **Testing**: Monthly backup verification reports; quarterly full restore drills; track success/failure in DR runbook with sign-off by SRE + Security.

## 5. Patch & Update Policy
- OS and hypervisor: monthly patch window (e.g., second Tuesday) with staging soak of 7 days; emergency CVE &#x2265; 8.0 patched within 48 hours.
- Kubernetes and cluster addons: minor versions quarterly; apply in staging then prod via blue/green node rotation; rollback by cordon/drain and revert node images.
- AION services: semantic-versioned images; deploy via canary then rolling; rollback by helm/ArgoCD to previous release and config snapshots.
- Middleware (PostgreSQL, Vector DB, MinIO): minor updates quarterly; major with approved change record and backup; rollback using snapshot + config restore.

## 6. Access Management & IAM
- **Roles/Groups**: `Admins` (break-glass), `PlatformOps`, `NetworkOps`, `DataOps`, `Security`, `ReadOnlyOps`, `Developers`, `ServiceAccounts` (scoped to namespace/service), `Auditors`.
- **Controls**: SSO with MFA required for all privileged roles; short-lived credentials via OAuth2/OIDC + service account tokens bound to namespaces; SSH disabled on app nodes, use bastion with cert-based auth.
- **Policies**: least-privilege RBAC in Kubernetes; database roles separated for app vs admin; object store buckets with IAM policies per environment; logging and access reviews monthly.
- **Lifecycle**: onboarding links to SOP; offboarding revokes SSO, VPN, cluster access, and rotates shared secrets; CMDB auto-updates via IdP webhooks.

## 7. Critical Services List & Recovery Priorities
| Service | Business Impact | Dependencies | Priority | Target RTO/RPO | HA/DR Notes |
| --- | --- | --- | --- | --- | --- |
| Gateway & Console | Customer-facing access to agents and catalog | LB, Kubernetes, PostgreSQL, Object store | P1 | RTO 2h / RPO 30m | Multi-node, active-active behind LB; restore via Helm rollback + DB recovery |
| Control Plane APIs (aion) | Orchestration and policy enforcement | Kubernetes, PostgreSQL, Vector DB | P1 | RTO 2h / RPO 30m | Run across 3+ replicas; DB HA pair; WAL restore for data |
| Task/Kernel Workers | Executes agent jobs | Kubernetes GPU nodes, Object store | P2 | RTO 4h / RPO 4h | Autoscale; drain/replace nodes; rebuild images from registry |
| Data Layer (PostgreSQL/Vector/Object) | Persistent state and artifacts | Storage cluster, network | P1 | RTO 4h / RPO 30m (DB), 4h (others) | Patroni or managed HA; cross-region object replication |
| Observability Stack | Monitoring, alerting, tracing | Kubernetes, storage, LB | P2 | RTO 6h / RPO 24h | Run in separate namespace/subnet; secondary snapshots; dashboards IaC |
| CI/CD & Artifact Registry | Build and image provenance | Git, registry storage, signing keys | P2 | RTO 6h / RPO 24h | Mirror registry; backup signing keys; runner HA |

- Recommendations: add automated IAM recertification, simulate DR twice per year with full failover, and enforce tag compliance gates in IaC pipelines.
