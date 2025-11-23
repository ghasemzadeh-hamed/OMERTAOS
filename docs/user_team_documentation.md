# User & Team Documentation

This guide centralizes user-facing and operational documentation for AION-OS, spanning installation, quickstart, UI usage, administration, FAQs, and glossary terminology. It complements existing deep dives in `docs/install`, `docs/quickstart.md`, and `docs/operations_and_support.md`.

## 1. Installation Guide

### Developer installation (local / sandbox)
- **Prerequisites**
  - OS: Ubuntu 22.04+, Debian 12+, macOS with Docker Desktop, or Windows 11 with WSL2 + Docker Desktop (WSL integration enabled).
  - Hardware: 4 CPU cores, 8 GB RAM, 10 GB free disk; GPU optional unless running vLLM overlay.
  - Network: Internet egress to pull container images and git; optional HTTPS proxy settings configured in Docker if required.
  - Software: Git, Docker Engine/Compose v2, PowerShell (Windows), Bash (Linux/macOS).
- **Steps**
  1) Clone the repository and enter the project root:
     ```bash
     git clone https://github.com/Hamedghz/OMERTAOS.git
     cd OMERTAOS
     ```
  2) Prepare environment variables (developer defaults):
     ```bash
     cp dev.env .env
     ```
  3) Launch the stack with the developer overlay:
     ```bash
     ./install.sh --profile user --local
     # Windows / WSL2
     pwsh ./install.ps1 -Profile user -Local
     ```
  4) Verify services:
     - `docker compose ps` shows gateway, control, console, and dependencies as `Up`.
     - Access console at `https://localhost:3000` (self-signed cert) and log in via seeded credentials if provided in `.env`.
- **Troubleshooting**
  - Run `./quick-install.sh` (`.ps1` on Windows) to regenerate `.env`, JWT keys, and dev certificates if the console fails TLS negotiation.
  - If compose pulls are slow, pre-fetch images with `docker compose pull` or configure a mirror in Docker daemon settings.
  - Ensure WSL integration is enabled and Docker Desktop is running before invoking PowerShell scripts.

### Production installation (server / cluster)
- **Prerequisites**
  - OS: Ubuntu Server 22.04 LTS (native) or a hardened host/VM with Docker Engine; Secure Boot/FDE recommended.
  - Hardware: 8+ CPU cores, 32+ GB RAM, SSD storage; GPUs for model-serving overlays; outbound TLS egress.
  - Network: Static IP or DNS entry for gateway/console; firewall ports open for HTTPS (443), API/gRPC as configured.
  - Accounts & permissions: sudo privileges, ability to configure systemd/NSSM, and (optionally) Kubernetes access for enterprise profile hooks.
- **Steps**
  1) Copy or template environment variables using `config/templates/.env.example` and profile defaults under `core/installer/profile/defaults/`.
  2) Run the installer with the target profile:
     ```bash
     sudo ./install.sh --profile enterprise --update
     # Optional: add --compose-overlay docker-compose.obsv.yml for observability
     ```
  3) On Windows hosts, execute from an elevated PowerShell prompt:
     ```powershell
     pwsh ./install.ps1 -Profile enterprise -Update
     ```
  4) Validate health:
     - `systemctl status aion-*` (native) or `docker compose ps` (containerized) shows running services.
     - Gateway responds on `https://<fqdn>`; console sign-in completes via configured IdP (NextAuth/LDAP/OAuth).
     - Logs from `/var/log/aionos-firstboot.log` confirm first-boot patching.
- **Configuration & version management**
  - Pin compose files and overlays via Git tags/releases; prefer semantic tags for reproducible rollouts.
  - Use `config/` manifests and `profiles/` docs to align feature flags, LDAP/Kubernetes hooks, and hardening levels.
  - Keep `.env` files per-environment and store secrets in Vault/KMS where available, injecting via environment at runtime.
- **Troubleshooting (production)**
  - If services fail to start, run `docker compose logs --tail=200 <service>` or check `journalctl -u aion-*` for native units.
  - For TLS issues, re-issue certificates or configure reverse proxies (nginx/traefik) as shown in `configs/` templates.
  - For database connectivity errors, confirm connection strings in `.env` and ensure network ACLs/security groups permit access.

## 2. Quickstart / Getting Started Guide
- **Objective:** Bring a new contributor or operator to a running stack in minutes.
- **Minimal path (Docker Compose quickstart)**
  1) `git clone ... && cd OMERTAOS`
  2) `./quick-install.sh` (Linux/macOS) or `./quick-install.ps1` (Windows) - auto-copies `dev.env` to `.env`, generates dev TLS/JWT keys, and starts compose.
  3) Open `https://localhost:3000` and follow the console setup wizard to confirm gateways and control APIs respond.
- **Sample command recap**
  ```bash
  ./quick-install.sh
  docker compose -f docker-compose.yml -f docker-compose.local.yml ps
  ```
- **Where to go next**
  - Configure agents via the catalog UI: `/agents/catalog`.
  - Deploy and monitor via "My Agents" page.
  - Review `docs/quickstart.md` for ISO/native/WSL flows and deeper tuning options.

## 3. End-User Manual / UI Guide
- **Audience:** Operators, data scientists, and platform users interacting through the Glass console.
- **Navigation & layout**
  - **Home / Dashboard:** High-level health, recent tasks, and quick links to catalog and policies.
  - **Agent Catalog (`/agents/catalog`):** Browse templates, fill recipe-driven forms, and preview deployment parameters.
  - **My Agents (`/agents/my-agents`):** View deployed agents, status, tenancy context, and actions (deploy, disable, patch config).
  - **Tasks / Runs:** Monitor job status, latency/throughput charts, and logs streamed via SSE/WebSockets.
  - **Policies:** Create/edit bundles, assign to agents, and review enforcement history.
  - **Settings:** Manage credentials, tokens, feature flags (e.g., LatentBox discovery), and regional settings (i18n/RTL).
- **Common workflows**
  - **Deploy an agent from catalog**
    1) Open `/agents/catalog`, pick a template.
    2) Complete form fields (model, tools, tenancy headers auto-filled from profile).
    3) Click **Deploy**; success shows new entry under **My Agents** with healthy status.
  - **Monitor a running agent**
    1) Navigate to **My Agents** &#x2192; select agent.
    2) Inspect live metrics, recent runs, and logs; download artifacts if exposed.
  - **Edit policy bindings**
    1) Go to **Policies**, open a bundle, adjust rules (auth, rate limits, tool access).
    2) Save and apply; confirmation banner appears and enforcement history updates.
- **Accessibility & shortcuts**
  - UI supports RTL and multilingual text; keyboard focus indicators are enabled by default.
  - Standard keyboard navigation: `Tab`/`Shift+Tab` to move, `Enter` to activate, `Esc` to close modals.
- **Screenshots**
  - Include console screenshots in `docs/assets/` (placeholders: `console-dashboard.png`, `agents-catalog.png`, `policy-editor.png`). Link them from this guide when available.

## 4. Admin Guide (System Administrator Guide)
- **Configuration management**
  - Centralize environment variables per tier (`.env` files), keeping secrets in Vault/KMS; use Docker/Kubernetes secrets to inject at runtime.
  - Profile toggles and feature flags live in `config/` and `config/agent_catalog/recipes`; keep them version-controlled.
- **Monitoring & observability**
  - Dashboards (Grafana/OTel) should track gateway/control latency, error rates, task throughput, queue depth, CPU/RAM/disk, and GPU utilization.
  - Alerts: P1 when API error rate >2% for 5 minutes; P2 when task queue age exceeds threshold; infra alerts on disk >85%.
- **Backup & restore**
  - Snapshot databases and object stores daily; retain 30 days. Test restores quarterly in staging.
  - Store backups encrypted; document restore commands per datastore (relational, vector, object) alongside verification steps (row counts, checksums).
- **Access control & user management**
  - Use NextAuth/IdP integration for SSO; enforce RBAC for operators vs. viewers.
  - Rotate credentials quarterly; disable stale accounts; audit login/logouts via gateway logs.
- **Upgrades & maintenance**
  - Perform rolling updates via `docker compose pull && docker compose up -d` (or Kubernetes rolling deployments) in staging before prod.
  - For native installs, use `./install.sh --update` to pull signed releases; confirm `/var/log/aionos-firstboot.log` for patches.
  - Keep kernels and model manifests aligned with registry versions; run smoke tests post-upgrade using scripts in `scripts/`.
- **Logs & diagnostics**
  - Standard log format: JSON with timestamp, service/component, level, trace/correlation IDs, request/agent IDs.
  - Aggregate via ELK/OTel Collector; retain 30-90 days per compliance.
  - For incidents, capture bundles (logs, configs, health endpoints) following `docs/operations_and_support.md` playbooks.

## 5. FAQ & Known Issues
- **FAQ**
  - *How do I reset my `.env` and dev certificates?* Run `./quick-install.sh` (or `.ps1`) to regenerate.
  - *Why does the console show TLS warnings?* Dev certificates are self-signed; trust locally or supply real certificates via reverse proxy configs.
  - *How do I enable GPU-backed models?* Use `docker-compose.vllm.yml` overlay and ensure NVIDIA drivers + `nvidia-container-toolkit` are installed.
  - *Can I run without internet?* Use ISO/offline cache instructions in `docs/install/iso.md`; ensure registries and compose images are pre-loaded.
  - *Where are hardware compatibility details?* See `docs/hcl/index.md` and related GPU/NIC matrices.
- **Known issues**
  - Self-signed certs may block some browsers &#x2192; workaround: import local CA or terminate TLS behind a trusted reverse proxy. *(Status: open; mitigated in production by real certs.)*
  - WSL networking quirks can block container DNS &#x2192; workaround: restart Docker Desktop, ensure `resolv.conf` points to valid DNS. *(Status: open)*
  - Long initial pulls on limited bandwidth &#x2192; workaround: mirror images locally or run `docker compose pull` before install. *(Status: open)*

## 6. Glossary / Key Terms
| Term | Definition | Context |
| ---- | ---------- | ------- |
| **AION-OS** | Hybrid operating system for autonomous AI agents combining kernels, control plane, gateway, and console. | Platform name |
| **Glass console** | Next.js UI for setup, catalog, policies, tasks, and monitoring. | UI/frontend |
| **Gateway** | TypeScript proxy handling API/auth/model traffic. | Services |
| **Control plane** | Python workers orchestrating memory, policies, and task routing. | Services |
| **Agent catalog** | Templates and recipes that drive deployable agents via UI/API. | UI & config |
| **Profile (user/pro/enterprise)** | Predefined install presets toggling features, ML tooling, and hardening. | Install/runtime |
| **LatentBox** | Feature-flagged tool discovery/sync capability driven by `config/latentbox/tools.yaml`. | Feature flag |
| **Policy bundle** | Set of enforcement rules applied to agents (auth, rate limits, tool access). | Security/control |
| **First-boot log** | `/var/log/aionos-firstboot.log` capturing initial patching and service enablement. | Operations |

---

**Maintenance & structure suggestions**
- Store this guide in `docs/user_team_documentation.md` and cross-link from `docs/README.md` for discoverability.
- Keep screenshots in `docs/assets/` with semantic names; update after major UI changes.
- Schedule quarterly doc reviews tied to release trains; update versioned examples and overlays as profiles evolve.
