# S4 deployment consolidation

S4 made `deploy/` the only maintained deployment owner. The separately approved
S5 phase subsequently retired the legacy recovery and compatibility inputs.

## Canonical ownership

- Native environment, lifecycle scripts and systemd units: `deploy/native/`
- Docker Compose definitions and lifecycle scripts: `deploy/docker/`
- Kubernetes manifests: `deploy/kubernetes/`
- Observability, CI, bundles and capability templates remain under their
  existing `deploy/` subdirectories.

Root `install*`, `run*`, `quick-install*` and `uninstall.sh` files are thin
delegators. Compose commands use `--project-directory .` so canonical files
nested under `deploy/docker/compose/` retain repository-root build contexts and
bind mounts.

## Compatibility and limitations

Root Compose files and deployment mirrors were retired in S5 after explicit
operator approval. New changes must be made only in the canonical paths;
architecture tests require the retired paths to remain absent.

Windows validation can prove Compose rendering, PowerShell contracts and static
file ownership. It cannot prove Linux permissions, package installation,
systemd activation, or live service health. No stack or persistent service is
started by this migration.

## Rollback

Revert the S4 and S5 change sets together to restore previous references and
compatibility payloads from Git. Persistent data and external service state are
not touched.
