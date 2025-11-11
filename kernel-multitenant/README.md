# Multi-Kernel Stack (User / Professional / Enterprise-VIP)

This package provides three switchable runtime profiles built on a shared gateway and control plane. It runs without Docker on Linux or Windows using Node.js 20+ and Python 3.10+.

## Quick Start

```bash
cd kernel-multitenant
make install
make run-user    # or run-pro / run-ent
```

Windows PowerShell:

```powershell
cd kernel-multitenant
.\scripts\install_windows.ps1
.\scripts\run_windows.ps1   # use $env:PROFILE=user|pro|ent before running
```

## Profiles at a Glance

| Profile          | Scheduler Tier | Control Policy Defaults | Notable Capabilities                                                          |
| ---------------- | -------------- | ----------------------- | ----------------------------------------------------------------------------- |
| `user`           | Shared/basic   | Local inference only    | Minimal ChatOps, no SEAL access                                               |
| `pro`            | Dedicated pods | Hybrid cloud policies   | Enables router policy overrides and staged rollouts                           |
| `enterprise-vip` | Isolated nodes | Enterprise guard rails  | Grants SEAL job orchestration (`POST /v1/seal/jobs`) and artifact replication |

Use `make run-user`, `make run-pro`, or `make run-ent` on Linux/macOS. On Windows, set `$env:PROFILE` accordingly before invoking `scripts\run_windows.ps1`.

## Installation Scripts

- Linux/macOS: `make install` bootstraps Python/Node environments without Docker.
- Windows: `scripts\install_windows.ps1` provisions dependencies, and `scripts\run_windows.ps1` launches the selected profile.
- `scripts/install_linux.sh` provisions the Python virtualenv and shared Node modules for Linux/macOS.

## Endpoints

- `GET /healthz` &#x2192; gateway liveness and SEAL flag.
- `POST /v1/config/{propose|apply|revert}` &#x2192; ChatOps configurator (admin token required).
- `POST /v1/router/policy/reload` &#x2192; refresh router and rollout policy.
- `POST /v1/seal/jobs` &#x2192; Enterprise-VIP only (requires `PROFILE=ent` and matching admin token).

## Acceptance Checklist

- Switch profiles using `make run-user`, `make run-pro`, or `make run-ent` without editing code.
- `GET /healthz` returns `{ ok: true }` across all profiles.
- `POST /v1/config/propose|apply|revert` persists pending configuration state to `configs/pending.json`.
- Enterprise-VIP profile enables SEAL endpoints, streams job status, and emits artifacts under `registry/storage/experiments/`.
- All files are ASCII-only and scripts support Linux/Windows without Docker.

## Directory Highlights

- `config/profiles/` - declarative kernel definitions inheriting from `kernel.base.yaml`.
- `deploy/` - future docker-compose overlays for CI orchestration.
- `shared/gateway/` - Express/TypeScript gateway with ChatOps and SEAL proxy routes.
- `shared/control/` - FastAPI control plane with profile loader, ChatOps configurator, and SEAL orchestration.
- `registry/` - artifact layout and indexer helper.
- `configs/` - rollout policies and SEAL defaults.
- `scripts/` - installation and runtime helpers (Linux/Windows).
