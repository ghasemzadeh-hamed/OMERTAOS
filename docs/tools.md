# AION-OS Auxiliary Tools

The auxiliary tool suite adds operational controls to the Control plane and Console. Each tool is optional and can be enabled/disabled via environment variables.

## Control plane APIs

| Module        | Endpoint prefix                      | Purpose                                                                                                                              |
| ------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| File Explorer | `/api/files`                         | List, create, delete, rename files within `AION_ALLOWED_PATHS`. Text editing available via `/api/files/content` + `/api/files/save`. |
| Data Studio   | `/api/data/preview`                  | Preview CSV/JSON payloads (limit configurable).                                                                                      |
| Config Center | `/api/config`, `/api/network/config` | Read merged configuration from `.env` & `config/aionos.yaml`; write overrides to YAML.                                               |
| Metrics       | `/api/metrics`                       | CPU, memory, disk, GPU, service & agent status. Exposes `/metrics` (Prometheus) when `AION_METRICS_ENABLED=1`.                       |
| Services      | `/api/services`                      | Inspect and control core services. Backends selected via `AION_SERVICE_CONTROL_MODE` (`docker`, `systemd`, `script`, `disabled`).    |
| Logs          | `/api/logs`                          | Enumerate streams and tail log files defined by `AION_LOG_STREAMS` or defaults in `./logs`.                                          |
| Auth admin    | `/api/auth`                          | List users/roles, assign roles, mint API tokens (requires Postgres via `DATABASE_URL`).                                              |
| Models        | `/api/models`                        | Manage local models in `AION_CONTROL_MODELS_DIRECTORY`. Registry file configurable through `AION_MODEL_REGISTRY`.                    |
| Datasets      | `/api/datasets`                      | Register/delete datasets tracked in `AION_DATASET_REGISTRY`.                                                                         |
| Packages      | `/api/packages`                      | Install/remove plugin packages based on `AION_PACKAGE_REGISTRY`.                                                                     |
| Backup        | `/api/backup`                        | Trigger archive snapshots into `AION_BACKUP_TARGET`. History stored under `AION_BACKUP_HISTORY`.                                     |
| Update Center | `/api/update`                        | Report current version, check remote feed (`AION_UPDATE_FEED_URL`), execute update script (`AION_UPDATE_SCRIPT`).                    |

RBAC guard rails use the `X-AION-Roles` header. Admin-only actions require `ROLE_ADMIN`; file mutations accept `ROLE_ADMIN` or `ROLE_DEVOPS`.

## Console navigation

The Next.js console exposes the tools under the **Tools** tab with glassmorphism UI. Each page talks to the Control plane REST APIs. Feature access is filtered by RBAC role (Managers see read-only tools, Admins receive mutation controls).

## Environment variables

Add the following to `.env` as needed:

```
AION_ALLOWED_PATHS=/models:/data:/logs:/config
AION_CONTROL_MODELS_DIRECTORY=./models
AION_MODEL_REGISTRY=config/model-registry.json
AION_DATASET_REGISTRY=config/datasets.json
AION_PACKAGE_REGISTRY=config/packages/registry.json
AION_PACKAGE_STATE=config/packages/installed.json
AION_BACKUP_TARGET=backups
AION_BACKUP_HISTORY=backups/history.json
AION_SERVICE_CONTROL_MODE=disabled
AION_SERVICE_CONTROL_SCRIPT=
AION_LOG_STREAMS=gateway:/var/log/aion/gateway.log,control:/var/log/aion/control.log
AION_METRICS_ENABLED=1
AION_METRICS_PROM_URL=
AION_UPDATE_FEED_URL=
AION_UPDATE_SCRIPT=scripts/update.sh
AION_GATEWAY_HEALTH_URL=http://gateway:3000/healthz
AION_CONTROL_HEALTH_URL=http://control:8000/healthz
AION_CONSOLE_HEALTH_URL=http://console:3000/healthz
AION_KERNEL_HEALTH_URL=http://kernel:7000/healthz
```

The Console supports embedding external dashboards via `NEXT_PUBLIC_PROM_URL`. Leave it unset to fall back to local metrics cards.

## CLI

The `aion-pkg` CLI provides basic package registry interactions:

```
aion-pkg list
aion-pkg install <name>
aion-pkg remove <name>
```

It operates on the same registry/state JSON files used by the Control plane APIs.
