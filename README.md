# 🧠 oMerTaOS AION

AION is a hybrid operating system for autonomous AI agents that links low-level kernels, a policy-aware control plane, and a web console into one cohesive platform. It runs consistently on bare metal, VMs, WSL, and containers, letting teams orchestrate agents and ML workloads across edge, cloud, and enterprise environments.

---

## Platform overview

- **Kernel + registry** — Rust kernels (`kernel/`, `kernel-multitenant/`) schedule tenant-aware agent tasks while registry definitions keep models and policies reproducible.
- **Control services** — Python workers under [`aion/`](aion) handle agent memory, task routing, and policy execution, backed by database and queue integrations defined in [`aion/config`](aion/config).
- **Gateway** — The TypeScript gateway in [`gateway/`](gateway) proxies API, auth, and model traffic between clients, the control plane, and model backends.
- **Console (Glass)** — The Next.js + React dashboard in [`console/`](console) delivers setup, monitoring, and policy automation with RTL/i18n, live task streams, and authenticated flows (NextAuth).
- **AI registry & models** — Registry manifests in [`ai_registry/REGISTRY.yaml`](ai_registry/REGISTRY.yaml) and model definitions in [`models/`](models) keep agent toolchains versioned and traceable.
- **Policies & agents** — Reference agents, policy bundles, and catalogs live under [`agents/`](agents), [`policies/`](policies), and [`config/agent_catalog`](config/agent_catalog), aligning runtime schemas with the console’s deployment wizards.

## Architecture at a glance

The platform is composed of interoperable services and dashboards:

- **Installer & profiles** — [`core/`](core) and [`config/`](config) render `.env` files, systemd/NSSM units, and profile defaults. Profiles (`user`, `pro`, `enterprise`) toggle ML tooling, Kubernetes hooks, LDAP, and hardening. [`configs/`](configs) and the `docker-compose.*.yml` overlays keep containerized deployments consistent.
- **Control plane classes & relationships** — The `aion` package organizes agents, memory, tasks, and workers into cohesive modules. Control APIs exposed through the gateway manage agent lifecycle (`/api/agents`), deployments (`/api/agents/{id}/deploy`), and catalog discovery (`/api/agent-catalog`). Catalog recipes and form schemas in [`config/agent_catalog/recipes`](config/agent_catalog/recipes) map directly to console wizards and validation logic.
- **Console dashboards** — The Glass console ships authenticated dashboards for agent catalogs, "My Agents", policy editors, task boards, latency/throughput telemetry, and LatentBox tool discovery. Its NextAuth setup covers credential and Google OAuth flows, uses TanStack Query for optimistic updates, and streams events via SSE/WebSockets for live task/status refreshes.【F:console/README.md†L1-L55】【F:console/README.md†L57-L78】
- **AI registry & model plumbing** — Registry entries referenced as `model://` are resolved through the gateway to runtime backends. Model manifests in [`models/`](models) stay aligned with registry metadata to guarantee deterministic builds and audits.
- **Security & compliance** — Hardening levels (`none`, `standard`, `cis-lite`) apply UFW, Fail2Ban, and Auditd. Secure Boot, full-disk encryption, and update cadence are documented under [`docs/security`](docs/security). First-boot automation patches hosts and captures logs at `/var/log/aionos-firstboot.log`.

## Quick start

### Linux (Docker Engine)

```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS
./install.sh --profile user            # or pro / enterprise-vip
```

- Add `--local` to target [`docker-compose.local.yml`](docker-compose.local.yml) for lightweight developer setups.
- Add `--update` to pull the latest commits before launching services.

### Windows 11 / WSL2

```powershell
git clone https://github.com/Hamedghz/OMERTAOS.git
Set-Location OMERTAOS
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
powershwll ./install.ps1
```

- Runs from Windows or WSL terminals; Docker Desktop must be enabled with WSL integration.
- Pass `-Local` for the developer overlay or `-Update` to fetch new commits.

### Fast path (Docker Compose quickstart)

- Copy [`dev.env`](dev.env) to `.env` (or let `quick-install.sh` / `quick-install.ps1` do it automatically).
- Generate dev certs/JWT keys and start the stack:

```bash
./quick-install.sh
```

```powershell
./quick-install.ps1
```

### Other flows

The ten-step playbook for ISO, native Linux, WSL, and Docker modes is in [`docs/quickstart.md`](docs/quickstart.md). ISO and native installers guard destructive actions with the `AIONOS_ALLOW_INSTALL` flag.

## Repository map

| Path | Purpose |
| ---- | ------- |
| [`aion/`](aion) | Python services and workers coordinating agent memory, policy execution, and task orchestration. |
| [`console/`](console) | Next.js + React Glass console with setup wizard, authenticated dashboards, and multilingual support. |
| [`gateway/`](gateway) | TypeScript gateway proxying API/auth/model traffic to control services and runtime backends. |
| [`core/`](core) | Installer assets, first-boot automation, kiosk tooling, and OS packaging logic. |
| [`kernel/`](kernel) / [`kernel-multitenant/`](kernel-multitenant) | Rust kernels and registry definitions for single- and multi-tenant scheduling. |
| [`scripts/`](scripts) | Automation utilities for quick setup, smoke tests, installers, and CI helpers. |
| [`config/`](config) / [`configs/`](configs) | Environment templates, systemd/NSSM units, reverse-proxy manifests, and profile wiring. |
| [`agents/`](agents) / [`policies/`](policies) | Reference agent definitions and policy bundles exercised by the runtime and console. |
| [`models/`](models) | Model manifests aligned with the AI registry for reproducible deployments. |
| [`ai_registry/`](ai_registry) | Central registry metadata consumed by gateways, agents, and policies. |

## Profiles

| Profile    | Default scope             | ML tooling      | Platform add-ons               | Hardening |
| ---------- | ------------------------- | --------------- | ------------------------------ | --------- |
| user       | Gateway, control, console | Disabled        | Docker (lightweight)           | none      |
| pro        | Gateway, control, console | Jupyter, MLflow | Docker                         | standard  |
| enterprise | Gateway, control, console | Jupyter, MLflow | Docker, Kubernetes hooks, LDAP | cis-lite  |

Profile manifests reside in [`config/profiles`](config/profiles) with defaults in [`core/installer/profile/defaults`](core/installer/profile/defaults). The installer pipeline renders `.env` files from [`config/templates/.env.example`](config/templates/.env.example) before first-boot automation enables services.

## Docker Compose overlays

[`docker-compose.yml`](docker-compose.yml) is the production baseline. Overlays extend it for focused scenarios:

- [`docker-compose.local.yml`](docker-compose.local.yml) – developer profile with lightweight defaults.
- [`docker-compose.obsv.yml`](docker-compose.obsv.yml) – adds observability tooling (OTel collector, dashboards).
- [`docker-compose.vllm.yml`](docker-compose.vllm.yml) – GPU-enabled vLLM runtime for large model experiments.

Combine overlays with `docker compose -f docker-compose.yml -f <overlay> up -d` to keep configurations in sync.

## Agent catalog and runtime wiring

- Agent templates live in [`config/agent_catalog/agents.yaml`](config/agent_catalog/agents.yaml) with per-template recipes in [`config/agent_catalog/recipes`](config/agent_catalog/recipes).
- Control APIs exposed via the gateway manage catalog discovery and agent lifecycle:
  - `GET /api/agent-catalog`, `GET /api/agent-catalog/{id}`
  - `GET /api/agents`, `POST /api/agents`, `PATCH /api/agents/{id}`, `POST /api/agents/{id}/deploy`, `POST /api/agents/{id}/disable`
- Console pages `/agents/catalog` and `/agents/my-agents` render dynamic forms from the same schemas and let users deploy agents with correct tenancy headers.
- LatentBox discovery (feature-flagged via `FEATURE_LATENTBOX_RECOMMENDATIONS`) hydrates an external tool registry from [`config/latentbox/tools.yaml`](config/latentbox/tools.yaml) and exposes sync/search endpoints alongside console UIs.

## Security, updates, and compliance

- First boot runs `apt-get update && apt-get upgrade` and `snap refresh`, then installs profile-specific services; logs persist at `/var/log/aionos-firstboot.log`.
- Secure Boot, full-disk encryption, and CIS-lite hardening are documented in [`docs/security`](docs/security), along with update cadence and CVE tracking.
- Installer flows gate destructive actions behind `AIONOS_ALLOW_INSTALL` and publish SBOM/signing steps described in [`docs/release.md`](docs/release.md).

## Hardware compatibility

Compatibility matrices (GPU, NIC, Wi‑Fi, firmware) and the reporting process live in [`docs/hcl`](docs/hcl). Detection scripts under `core/installer/bridge/tasks` keep hardware checks automated.

## Documentation hub

Enterprise-facing runbooks start at [`docs/README.md`](docs/README.md): quickstart guides, install modes, profiles, security baselines, troubleshooting, release, privacy, and hardware compatibility.

## Contributing and license

Please review [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md) before submitting changes. AION-OS is distributed under the [Apache 2.0 license](LICENSE).
