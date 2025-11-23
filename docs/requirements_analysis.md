# OMERTAOS Requirements Analysis

## 1. Functional Requirements
| ID | Description | Actors | Acceptance Criteria |
| -- | ----------- | ------ | ------------------- |
| FR-1 | Provide guided installation with selectable profiles (user, pro, enterprise) across Linux, Windows/WSL, and Docker overlays. | Operators, Platform Engineers | Install completes with profile defaults applied, .env rendered, services start without errors, and logs captured for first-boot; destructive actions gated by `AIONOS_ALLOW_INSTALL`. |
| FR-2 | Expose control plane APIs for agent lifecycle management (create, list, update, deploy, disable). | Operators, Data Scientists, Gateway | API endpoints respond with correct status codes, validate schemas, update runtime state, and changes reflect in console "My Agents" view. |
| FR-3 | Deliver agent catalog discovery with recipe-driven forms and validation. | Operators, Data Scientists, Console | Catalog endpoints and UI render available agents, enforce required fields, and allow deployment with tenancy headers; invalid inputs return actionable errors. |
| FR-4 | Manage model and AI registry resolution for deterministic deployments. | Gateway, Control Services, Platform Engineers | Registry entries resolve `model://` references to configured backends; manifests are versioned and validated before deployment with reproducibility logs. |
| FR-5 | Stream task metrics, status, and logs to dashboards with live updates. | Operators, Console | SSE/WebSocket streams surface task state changes within target latency; dashboards refresh without manual reload and expose latency/throughput charts. |
| FR-6 | Enforce policy bundles on agents with auditability. | Security Team, Control Services | Policies can be attached/enforced per agent, violations are logged, and compliance coverage is reportable via APIs/console. |
| FR-7 | Support LatentBox tool discovery when feature flag enabled. | Operators, Console, External Tool Registry | Tool catalog syncs from `config/latentbox/tools.yaml`, search endpoints and UI are available, and feature can be toggled without affecting baseline flows. |
| FR-8 | Provide authenticated console with multilingual support and setup wizard. | Operators, Admins | Users can sign in (credentials/OAuth), navigate localized dashboards, complete setup, and session handling meets security requirements. |
| FR-9 | Offer hardware compatibility references and detection scripts during install. | Platform Engineers, Operators | Compatibility matrices are accessible, detection tasks run during install, and blockers are reported with remediation guidance. |

## 2. Non-Functional Requirements
### Performance & Scalability
| ID | Description | Target/Metric | Data Source | Owner |
| -- | ----------- | ------------- | ----------- | ----- |
| NFR-P1 | Dashboard refresh latency for task/metric streams. | P95 < 3s | Console telemetry (SSE/WebSocket metrics) | Frontend Lead |
| NFR-P2 | Agent deployment throughput. | &#x2265;98% successful deployments weekly | Gateway/control deployment logs | Control Engineering |
| NFR-P3 | Installer total time to first running stack. | &#x2264;30 minutes (user), &#x2264;60 minutes (enterprise) | Installer logs and onboarding surveys | Platform/DevOps |

### Availability & Reliability
| ID | Description | Target/Metric | Data Source | Owner |
| -- | ----------- | ------------- | ----------- | ----- |
| NFR-A1 | Service uptime for core control/gateway stack. | &#x2265;99% during supported hours | Uptime monitors, compose/K8s health checks | SRE/DevOps |
| NFR-A2 | Graceful failure and restart of workers/proxies. | Automatic restart on failure; no data loss for acknowledged tasks | Process supervisors (systemd/NSSM), queue metrics | Control Engineering |

### Security
| ID | Description | Target/Metric | Data Source | Owner |
| -- | ----------- | ------------- | ----------- | ----- |
| NFR-S1 | Authentication and authorization across console and APIs. | All endpoints require auth; role/tenant scoping enforced | Auth logs, gateway middleware audits | Security Engineering |
| NFR-S2 | Hardening profiles applied per installation tier. | Profile defaults enforce UFW/Fail2Ban/Auditd; CIS-lite for enterprise | First-boot logs, hardening scans | Security/DevOps |
| NFR-S3 | Transport and secret security. | TLS for external endpoints; secrets stored in env files/secret stores with rotation guidance | Gateway cert management, secret scan reports | Security Engineering |
| NFR-S4 | Audit logging for policy enforcement and agent actions. | 100% policy decisions and agent lifecycle events logged | Control plane audit trails | Security/Compliance |

### Usability
| ID | Description | Target/Metric | Data Source | Owner |
| -- | ----------- | ------------- | ----------- | ----- |
| NFR-U1 | Console accessibility and localization. | Supports RTL/i18n; key workflows localized | Console UX audits, locale coverage reports | Frontend Lead |
| NFR-U2 | Error feedback for catalog/forms and installs. | Validations provide actionable messages; <2% user support tickets per deployment | Support system, telemetry on validation failures | Product/UX |

### Maintainability
| ID | Description | Target/Metric | Data Source | Owner |
| -- | ----------- | ------------- | ----------- | ----- |
| NFR-M1 | Configuration consistency across profiles/overlays. | Docker/K8s overlays render from shared templates with validation in CI | CI pipeline results, template checks | Platform/DevOps |
| NFR-M2 | Registry/model reproducibility. | 100% manifests validated and versioned before deployment | CI/CD registry validation reports | Control Engineering |
| NFR-M3 | Documentation coverage for installers, security, and catalog schemas. | Up-to-date docs in `docs/` and console README; reviewed each release | Documentation review checklist | Product/Docs |

## 3. Constraints
- **Technology:**
  - Kernels and schedulers implemented in Rust (`kernel/`, `kernel-multitenant/`).
  - Control plane services in Python (`aion/`); gateway in TypeScript (`gateway/`); console in Next.js/React (`console/`).
  - Environment templating and installers rely on Compose/Kubernetes overlays and profile manifests.
- **Infrastructure:**
  - Supports bare metal, VMs, WSL2, and Docker; Kubernetes hooks available for enterprise profiles.
  - Hardware must meet documented compatibility matrices; GPU/NIC/Wi-Fi support dependent on `docs/hcl` guidance.
  - Requires Docker Engine or Docker Desktop for containerized modes; network access for updates and external tool registry when features enabled.
- **Regulatory/Compliance:**
  - Security hardening aligns with CIS-lite guidance for enterprise profile; assumes organizational compliance ownership beyond provided docs.
  - SBOM/signing steps documented in release process; assumes adopters handle formal certifications (e.g., SOC2/ISO) externally.

## 4. Requirements Traceability Matrix (RTM)
| Requirement ID | Design/Artifact Reference | Test Coverage | Responsible Team |
| -------------- | ------------------------- | ------------- | ---------------- |
| FR-1, FR-9 | Installer assets in `core/`, `config/`, `configs/`; `docs/quickstart.md`, hardware compatibility docs | Installer smoke tests, hardware detection scripts | Platform/DevOps |
| FR-2, FR-4, FR-6 | Control services in `aion/`, gateway routes in `gateway/`, registry manifests in `ai_registry/`, `models/`, policy bundles in `policies/` | API/worker unit tests, registry validation CI, policy enforcement tests | Control Engineering, Security |
| FR-3, FR-5, FR-7, FR-8 | Console flows in `console/`, catalog schemas in `config/agent_catalog/`, latentbox tools config | Frontend unit/e2e tests, telemetry dashboards, feature-flag tests | Frontend, Product/UX |
| NFR-P1, NFR-U1 | Console performance budgets and i18n settings in `console/README.md` and implementation | Performance tests, localization audits | Frontend |
| NFR-P2, NFR-P3, NFR-M1 | CI pipelines, compose overlays (`docker-compose*.yml`), installer logs | Deployment smoke tests, CI validation | Platform/DevOps |
| NFR-S1-S4, NFR-A1-A2 | Auth middleware, hardening scripts, monitoring configs | Security scans, uptime monitors, audit log checks | Security/DevOps |
| NFR-M2-M3 | Registry/model validation workflows, documentation in `docs/` and `console/README.md` | CI validation, doc review checklist | Control Engineering, Product/Docs |
