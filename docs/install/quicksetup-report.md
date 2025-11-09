# QuickSetup consolidation report

This report summarizes the audit of AION-OS installation and quick setup scripts and documents the
new standard entrypoints introduced in `scripts/quicksetup.sh` (Linux/macOS) and
`scripts/quicksetup.ps1` (Windows).

## Existing scripts before consolidation

| Path | Purpose | Observations | Action |
| ---- | ------- | ------------ | ------ |
| `install.sh` | Docker-based bootstrap with profile selection and telemetry toggles. | Contained the most complete logic but duplicated environment rendering and compose handling. | Replaced by wrapper that delegates to `scripts/quicksetup.sh`. |
| `install.ps1` | Windows interactive setup (clone/pull, env rendering, compose guidance). | Overlapped with new PowerShell logic and diverged from Linux flow. | Replaced by wrapper that calls `scripts/quicksetup.ps1`. |
| `scripts/install.sh` | Minimal Node/PNPM bootstrap for console builds. | Incomplete for modern stack; no config rendering. | Deprecated and redirected to QuickSetup. |
| `scripts/install.ps1` | Equivalent minimal Windows bootstrap. | Incomplete and inconsistent with Docker flow. | Deprecated and redirected to QuickSetup. |
| `scripts/install_linux.sh` | Native Linux service installer (systemd, PostgreSQL/Redis provisioning). | Still useful for legacy native deployments but not aligned with container-first QuickSetup. | Marked as deprecated with guidance to use QuickSetup for container installs. |
| `scripts/install_win.ps1` | Native Windows service installer (NSSM). | Legacy support path; heavy requirements. | Marked as deprecated pending redesigned native pipeline. |
| `scripts/install_module.sh` | Installs module bundles via ORAS/Cosign. | Still valid specialist tooling. | Left untouched (referenced in documentation). |
| `scripts/install_llm.sh` / `scripts/install_local_llm.sh` / `scripts/install_vllm_gpu.sh` | Helper utilities for model staging. | Not entrypoints; invoked manually. | Left untouched. |
| `tools/preflight.sh` | Environment prerequisite checks. | Already invoked by Docker installer. | Automatically called from QuickSetup when available. |
| `cli/install.py` | Python CLI helper for provisioning modules. | Orthogonal to stack bootstrap. | Left untouched. |

## Coverage of services and dependencies

The legacy installers touched disparate components:

- **Docker Compose stack** – `install.sh` handled `.env` creation, profile selection (user/pro/enterprise),
  telemetry toggles, and `docker compose up -d` with retries.
- **Service configuration** – `config/aionos.config.yaml` was created only by the bash installer; other
  scripts left gaps.
- **Telemetry** – Environment variables `AION_TELEMETRY_OPT_IN` and `AION_TELEMETRY_ENDPOINT` were set
  inconsistently across scripts.
- **Local model provisioning** – Bash installer optionally pulled Ollama models. Windows script offered
  no equivalent guard.
- **Native installers** (`scripts/install_linux.sh`, `scripts/install_win.ps1`) – provisioned systemd/NSSM
  units, PostgreSQL/Redis, and Node/PNPM builds. These flows remain legacy and are now labeled as such.

## Standard QuickSetup architecture

The new QuickSetup scripts implement a unified workflow:

- `scripts/quicksetup.sh`
  - ASCII-only prompts and logging.
  - Validates presence of `git`, `docker`, and either `curl` or `wget`.
  - Supports `--profile`, `--local`, `--compose-file`, `--noninteractive`, `--update`, `--repo`, and
    `--branch` flags.
  - Copies `.env` from `config/templates/.env.example` and normalizes profile/telemetry variables.
  - Persists `.aionos/profile.json` metadata and seeds `config/aionos.config.yaml`.
  - Invokes `tools/preflight.sh` when available, installs optional Ollama models, and starts the stack
    via Docker Compose with retries.
- `scripts/quicksetup.ps1`
  - Mirrors the bash behaviour for Windows users, including optional repository update/clone and
    profile metadata.
  - Detects Docker Compose v2 or classic `docker-compose`, enforces prerequisites, and shares the
    same configuration defaults.

## Deprecations and redirects

- Root-level `install.{sh,ps1}` now proxy directly to the QuickSetup scripts.
- Legacy helper installers print a `DEPRECATED` warning and delegate to QuickSetup when possible.
- Native service installers remain available but are clearly marked as legacy so that future work can
  replace them with modular helpers sourced from `scripts/lib/common.sh`.

## Next steps

1. Validate QuickSetup across the three supported profiles (`user`, `professional`, `enterprise-vip`).
2. Add automated smoke tests (CI matrix) that exercise QuickSetup with `--noninteractive` for Linux and
   Windows PowerShell environments.
3. Incrementally extract shared logic from legacy native installers into reusable modules under
   `scripts/lib/`.
