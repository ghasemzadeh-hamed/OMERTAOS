# CAPO native deployment profile

CAPO is the additive, Docker-independent deployment profile for an already
installed Debian or Ubuntu system on SSD. It preserves the canonical request
flow and repository ownership:

```text
console/ :3000 -> gateway/ :8080 -> control/ :8000 -> runtime-daemon/ :50051
                                              |
                         data/ registry/ schemas/ deploy/
```

CAPO does not partition or format disks, replace the existing Docker
Quickstart, migrate legacy directories, or change application APIs. Native
Linux commands are introduced in later phases and must not be run on Windows.

## Platform and paths

- Supported target: Debian 12 or Ubuntu 22.04/24.04 with systemd.
- Repository default: `/opt/omertaos/OMERTAOS`.
- Service account: dedicated, non-login `omertaos` user and group.
- Configuration: `/etc/omertaos/omertaos.env`, created by an operator from
  `CAPO.env.example`; the real file and real secrets never belong in Git.
- Persistent application data: `/var/lib/omertaos`.
- Logs and service lifecycle: systemd/journald.

The repository checkout and build outputs must be readable by `omertaos`.
Writable state belongs under `/var/lib/omertaos`, not in the source checkout.

## Scaffold

| Path | Purpose | Planned phase |
|---|---|---:|
| `CAPO.env.example` | Non-secret native configuration contract | 2 |
| `scripts/install-os-packages.sh` | OS dependency installer | 3 |
| `scripts/install-data-services.sh` | PostgreSQL/Redis setup | 3 |
| `scripts/install-python-control.sh` | Control environment/install | 4 |
| `scripts/install-node-services.sh` | Gateway and Console install/build | 4 |
| `scripts/install-rust-runtime.sh` | Runtime build/install | 4 |
| `scripts/{setup-systemd,first-boot,run-all,stop-all}.sh` | Lifecycle | 5 |
| `systemd/` | Four units and aggregate target | 5 |
| `scripts/smoke-test.sh`, `tests/` | Native/static validation | 6 |

Only phase-owned files are added in each run. Placeholder directories contain
their contract now; executable scripts and units are not fabricated early.

## Safety and idempotency contract

Every CAPO script must:

1. use `set -euo pipefail`, validate the target OS and required arguments, and
   provide `--help` plus a non-mutating `--dry-run` where it performs changes;
2. check current state before changing it and produce the same valid result on
   repeated runs;
3. fail with an actionable non-zero exit instead of suppressing errors with a
   blanket `|| true`;
4. limit privilege elevation to reviewed package, account, path, PostgreSQL,
   and systemd operations on the Linux target;
5. preserve an existing `/etc/omertaos/omertaos.env` and never print secrets;
6. never use destructive disk commands, delete repository/data paths, or
   depend on Docker for native service readiness.

The automation host is Windows. Commands involving `sudo`, package managers,
systemd, or native data services may be stored after review but are never
executed there. Native acceptance remains pending until proven on the intended
Linux SSD host.

## Required and optional data services

PostgreSQL and Redis are required. MongoDB, Qdrant, and MinIO are optional and
default to disabled. If an optional service is unavailable, Control must start
in an explicit degraded mode, report that capability unavailable in health or
diagnostics, and reject dependent operations clearly. It must not silently use
an in-memory substitute, weaken authorization, or make Console/Gateway bypass
Control. Set `CAPO_MONGO_ENABLED=true`, `CAPO_QDRANT_ENABLED=true`, or
`CAPO_MINIO_ENABLED=true` only after configuring and validating the matching
endpoint and credentials.

## Operator sequence

The finished profile is used in this order: copy and secure the environment
file, install OS/data dependencies, install application components, install the
systemd units, then run first-boot and smoke validation. Phase 3 installers and
their rollback/security notes are documented in
`../../docs/capo/native-os-data-installers.md`; later steps remain contracts
until their owning phases land.

See `PHASE_STATUS.md` for durable progress and
`../../docs/capo/repository-audit.md` for the audited entrypoints and legacy
assets. Human review is required before using CAPO on a production host.
