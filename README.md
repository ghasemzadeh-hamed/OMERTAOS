# 🧠 AION-OS (Hybrid AI Platform for Autonomous Agents)
AION-OS is a hybrid, modular operating system designed for **building, orchestrating, and scaling intelligent AI agents across bare-metal, virtualized, and web environments.**
It unifies kernel-level control, web-based orchestration, and developer SDKs into one cohesive platform — enabling seamless integration between Edge, Cloud, and Enterprise deployments.
________________________________________
## 🚀 Core Highlights
•	Unified Architecture — One shared kernel and deployment model for native Linux, ISO/Kiosk, WSL, and containerized runtimes.
•	Agent-Centric Design — Native runtime for multi-agent orchestration with memory, model, and policy subsystems.
•	Web-OS Console — Browser-based management UI (Next.js + React) for setup, monitoring, and policy automation.
•	AI Registry — Built-in model, algorithm, and service registry for reproducible, self-signed deployments.
•	Adaptive Profiles — User, Professional, and Enterprise tiers with modular service activation.
•	Security & Hardening — First-boot patching, role-based access, optional secure boot, and encrypted storage.
•	Developer SDK & CLI — Full Python/TypeScript SDK and CLI tools for building custom agents and control modules.


## Quick start

A short quick-start for each supported mode is available in [`docs/quickstart.md`](docs/quickstart.md). Each flow is designed to reach a working environment in ten steps or fewer.

| Mode | Summary |
| --- | --- |
| ISO / Kiosk | Boot the kiosk ISO, follow the wizard, and allow gated disk actions with `AIONOS_ALLOW_INSTALL=1`. |
| Native Linux | Bootstrap from a minimal Ubuntu base, run the installer bridge, and reuse the same wizard as the ISO. |
| Windows / WSL | Launch the wizard without disk actions, apply a profile, and start services through WSL integration. |
| Docker | Bring the stack up with Compose, pick a profile, and validate services through the embedded console. |

## Profiles

| Profile | Default scope | ML tooling | Platform add-ons | Hardening |
| --- | --- | --- | --- | --- |
| user | Gateway, control, console | Disabled | None | none |
| pro | Gateway, control, console | Jupyter, MLflow | Docker | standard |
| enterprise | Gateway, control, console | Jupyter, MLflow | Docker, Kubernetes hooks, LDAP | cis-lite |

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
- Troubleshooting, release, and privacy references.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for contribution guidelines and community expectations. Security-sensitive reports should follow [SECURITY.md](SECURITY.md).

## License

AION-OS is distributed under the [Apache 2.0 license](LICENSE).
