# Agent-OS AI Registry

This directory contains a self-updating metadata registry for models, algorithms, and services
used by Agent-OS deployments. It mirrors the structure described in `docs/agentos_ai_registry.md`
and includes manifests, policy configuration, installer utilities, and GitHub automation.

## Layout

- `REGISTRY.yaml` – top-level catalog index used by automation tools.
- `registry.lock.json` – content hash manifest for reproducible deployments.
- `models/`, `algorithms/`, `services/` – categorized metadata manifests.
- `scripts/` – Python utilities for catalog maintenance and installations.
- `config/` – policy configuration files for updates and installs.
- `security/` – minisign public keys and integrity material.
- `.github/workflows/` – CI workflow that keeps the registry synchronized.

Refer to the documentation for usage examples and integration guidance.
