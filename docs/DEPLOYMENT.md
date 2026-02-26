# DEPLOYMENT

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Docker Build
Use repository Dockerfiles and deployment scripts in `deploy/` and service subdirectories.

## Docker Compose
- Base compose: `deploy/docker-compose.yml` (and root compose overlays where applicable)
- CI/local overlays in `deploy/compose/`

Example:
```bash
docker compose -f deploy/docker-compose.yml up -d
```

## Helm Deployment
Helm and Kubernetes manifests are under `deploy/k8s/`.
- adapt values for tenant/profile/environment
- ensure secrets and policy bundles are mounted consistently

## Required Environment Variables
Typical required categories:
- control/gateway base URLs and auth tokens
- database/cache/storage endpoints (MongoDB/Redis/MinIO/Postgres as configured)
- registry and model resolver settings
- tenancy and policy toggles

## Production Configuration
- use hardened profile defaults
- enforce secret management (no plaintext in repo)
- pin registry lock and deployment artifact versions

## Scaling Strategy
- horizontal scale: stateless control/gateway replicas
- worker pools by workload class
- separate big-data compute from control-plane runtime nodes

## Runtime Daemon

Deploy and supervise `runtime-daemon` alongside control services; default bind `127.0.0.1:50051`.

