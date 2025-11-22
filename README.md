# 🧠 oMerTaOS AION (Hybrid AI Platform for Autonomous Agents)

AION is a hybrid, modular operating system designed for **building, orchestrating, and scaling intelligent AI agents across bare-metal, virtualized, and web environments.**
It unifies kernel-level control, web-based orchestration, and developer SDKs into one cohesive platform — enabling seamless integration between Edge, Cloud, and Enterprise deployments.

---

## 🚀 Core Highlights

• Unified Architecture — One shared kernel and deployment model for native Linux, ISO/Kiosk, WSL, and containerized runtimes.
• Agent-Centric Design — Native runtime for multi-agent orchestration with memory, model, and policy subsystems.
• Web-OS Console — Browser-based management UI (Next.js + React) for setup, monitoring, and policy automation.
• AI Registry — Built-in model, algorithm, and service registry for reproducible, self-signed deployments.
• Adaptive Profiles — User, Professional, and Enterprise tiers with modular service activation.
• Security & Hardening — First-boot patching, role-based access, optional secure boot, and encrypted storage.
• Developer SDK & CLI — Full Python/TypeScript SDK and CLI tools for building custom agents and control modules.

## Quick start

Use the repository-provided wrappers for the fastest path to a containerized deployment. Both scripts validate prerequisites (Git, Docker Engine/Compose, Python 3.11+) and keep the `.env` file, policy directory, and volume mounts in sync with [`scripts/quicksetup.sh`](scripts/quicksetup.sh) and [`scripts/quicksetup.ps1`](scripts/quicksetup.ps1).

### Linux (Docker Engine)

```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS
./install.sh --profile user            # or professional / enterprise-vip
```

- Append `--local` to target [`docker-compose.local.yml`](docker-compose.local.yml) for lightweight developer setups.
- Pass `--update` to fetch the latest commits before starting services.

### Windows 11 / WSL2

```powershell
git clone https://github.com/Hamedghz/OMERTAOS.git
Set-Location OMERTAOS
pwsh ./install.ps1 -Profile user       # or professional / enterprise-vip
```

- The script runs from either Windows or WSL terminals. Docker Desktop must be running with WSL integration enabled.
- Provide `-Local` for the developer profile or `-Update` to pull new commits before launch.

### Other flows

A ten-step playbook for every supported mode (ISO, native Linux, WSL, Docker) lives in [`docs/quickstart.md`](docs/quickstart.md). The ISO wizard and native installer flows continue to gate destructive actions on the `AIONOS_ALLOW_INSTALL` flag.

### Fast path (Docker Compose quickstart)

- Copy [`dev.env`](dev.env) to `.env` (or let `quick-install.sh` / `quick-install.ps1` do it for you).
- Generate development certs and JWT keys plus start the stack with Docker Compose:

```bash
./quick-install.sh
```

```powershell
./quick-install.ps1
```

## Repository structure

| Path | Description |
| ---- | ----------- |
| [`aion/`](aion) | Python services and workers that coordinate agent memory, policy, and task execution. |
| [`console/`](console) | Next.js + React management UI, including the setup wizard and operational dashboards. |
| [`gateway/`](gateway) | TypeScript API gateway that proxies model, policy, and control traffic between clients and the core runtime. |
| [`core/`](core) | Installer assets, first-boot automation, kiosk tooling, and OS packaging logic. |
| [`kernel/`](kernel) & [`kernel-multitenant/`](kernel-multitenant) | Rust-based kernels and registry definitions for single- and multi-tenant agent scheduling. |
| [`scripts/`](scripts) | Automation utilities (quick setup, smoke tests, native installers, CI helpers). |
| [`config/`](config) & [`configs/`](configs) | Environment templates, systemd units, NSSM definitions, and sample reverse-proxy manifests. |
| [`agents/`](agents) & [`policies/`](policies) | Reference agent definitions, policy bundles, and examples that exercise the runtime. |
| [`models/`](models) | Model manifests aligned with the AI registry for reproducible deployments. |


## Agent Catalog (templates + runtime wiring)

- Catalog definitions live in [`config/agent_catalog/agents.yaml`](config/agent_catalog/agents.yaml) with per-template recipes under
  [`config/agent_catalog/recipes`](config/agent_catalog/recipes).
- Control API surface:
  - `GET /api/agent-catalog` and `GET /api/agent-catalog/{id}` expose templates and recipes.
  - `GET /api/agents`, `POST /api/agents`, `PATCH /api/agents/{id}`, `POST /api/agents/{id}/deploy`, `POST /api/agents/{id}/disable`
    manage tenant-scoped agent instances with schema validation.
- Console pages under `/agents/catalog` and `/agents/my-agents` allow browsing templates, filling dynamic config forms, and
  deploying agents without leaving the UI (works with `TENANCY_MODE` single or multi-tenant headers).

## Docker Compose overlays

`docker-compose.yml` is the canonical definition for the production stack. Overlays extend it for targeted scenarios:

- [`docker-compose.local.yml`](docker-compose.local.yml) – local-only developer profile with lightweight defaults.
- [`docker-compose.obsv.yml`](docker-compose.obsv.yml) – optional observability extras (OTel collector, dashboards).
- [`docker-compose.vllm.yml`](docker-compose.vllm.yml) – GPU-enabled vLLM runtime for larger model experiments.

Use overlays with `docker compose -f docker-compose.yml -f <overlay> up -d` to avoid drifting configurations.

## Profiles

| Profile    | Default scope             | ML tooling      | Platform add-ons               | Hardening |
| ---------- | ------------------------- | --------------- | ------------------------------ | --------- |
| user       | Gateway, control, console | Disabled        | Docker (lightweight)           | none      |
| pro        | Gateway, control, console | Jupyter, MLflow | Docker                         | standard  |
| enterprise | Gateway, control, console | Jupyter, MLflow | Docker, Kubernetes hooks, LDAP | cis-lite  |

Profile definitions live in [`config/profiles`](config/profiles) and [`core/installer/profile/defaults`](core/installer/profile/defaults). The installer pipeline renders `.env` files from [`config/templates/.env.example`](config/templates/.env.example), and first-boot automation turns profile bits into services.

## Security and updates

- First boot runs `apt-get update && apt-get upgrade` and `snap refresh`, then installs profile-specific services. Logs are persisted in `/var/log/aionos-firstboot.log`.
- Optional hardening levels (`none`, `standard`, `cis-lite`) enable UFW, Fail2Ban, and Auditd according to profile needs.
- Secure Boot and full-disk encryption can be toggled from the wizard storage step; implementation details are covered in [`docs/security/secure-boot-fde.md`](docs/security/secure-boot-fde.md).
- CVE tracking and update cadence are described in [`docs/security/updates.md`](docs/security/updates.md), with the baseline checklist in [`docs/security/baseline.md`](docs/security/baseline.md).

## Hardware compatibility

Compatibility guidance and the reporting process live in [`docs/hcl`](docs/hcl). The GPU and NIC matrices are curated for Ubuntu AI class hardware with automated detection scripts under `core/installer/bridge/tasks`.

## Documentation

All enterprise-facing documentation is rooted at [`docs/README.md`](docs/README.md):

- Quick start playbooks for every install mode.
- Installation guides per mode (`docs/install`).
- Profile descriptions (`docs/profiles`).
- Security baseline and update guidance (`docs/security`).
- Hardware compatibility matrix (`docs/hcl`).
- AI registry catalog (`ai_registry/REGISTRY.yaml`) used by agent templates and policies via `model://` references.
- Troubleshooting, release, and privacy references.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for contribution guidelines and community expectations. Security-sensitive reports should follow [SECURITY.md](SECURITY.md).

## License

AION-OS is distributed under the [Apache 2.0 license](LICENSE).
