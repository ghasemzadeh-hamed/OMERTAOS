# Gate S4 report — Deployment Consolidation

Date: 2026-07-15

Branch: `capo-structure`

Status: **passed after approved S5 retirement and independent re-run**

## Gate result

Canonical Native, Docker and Kubernetes ownership exists under `deploy/`, and
the supported Compose definitions render successfully. Gate S4 additionally
requires every deployment payload under the following legacy locations to be
absent. The Git index still contains 84 non-empty payloads:

| Legacy location | Tracked paths checked | Non-empty deployment payloads |
|---|---:|---:|
| Deployment content under `execution/` | 70 | 70 |
| `docker/` | 1 | 1 |
| `infra/` | 4 | 4 |
| `core/systemd/` | 4 | 4 |
| `scripts/deploy/` | 5 | 5 |
| **Total** | **84** | **84** |

The `execution/` payloads include Compose, Kubernetes, systemd, CI, installer,
bundle, observability and capability-template mirrors. The other roots contain
the catalog Compose definition, Linux installer/service assets, systemd links,
and deployment-script links. Git object sizes were used so Windows symlink
materialization could not produce false zero-byte results.

These inputs were preserved during the first run because S4 did not authorize
file deletion. The operator then explicitly approved S5 retirement. After the
84 payloads and their empty roots were removed, the same filesystem check found
zero legacy deployment paths. Gate S4 therefore passed on re-run.

## Re-run result after S5

| Required-absent path | Result |
|---|---|
| `execution/` | Absent |
| `docker/` | Absent |
| `infra/` | Absent |
| `core/systemd/` | Absent |
| `scripts/deploy/` | Absent |

Final Gate S4 result: **passed**.

## Validation

| Area | Command / evidence | Result |
|---|---|---|
| Quickstart Compose | `docker compose --project-directory . -f deploy/docker/compose/quickstart.yml config --quiet` | Passed |
| Local Compose | `docker compose --project-directory . -f deploy/docker/compose/local.yml config --quiet` | Passed |
| Full Compose | `docker compose --project-directory . -f deploy/docker/compose/full.yml config --quiet` | Passed; unset optional Vault token warning |
| S4 architecture contract | `python -m pytest tests/architecture/test_deployment_consolidation.py -q` | 4 passed |
| Architecture regression | `python -m pytest tests/architecture -q -k "not test_structure_migration_gate"` | 60 passed, 1 deselected |
| CAPO deployment contract | `powershell -NoProfile -File deploy/CAPO/tests/contract-tests.ps1` | Passed |

No Compose stack, installer, systemd unit, persistent service or deployment was
started. Linux shell syntax, systemd behavior and live Native/Quickstart health
remain unproven on this Windows host.

## Security, migration and rollback

No database, data, auth, secret or external service state changed. S5 deletion
was performed only after explicit operator approval and preserved canonical
owners plus Git recovery history. Revert the S4/S5 change set together if the
retired compatibility paths must be restored.
