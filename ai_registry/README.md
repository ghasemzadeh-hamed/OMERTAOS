# Agent-OS AI Registry

The AI Registry stores metadata for models, algorithms, and services that AION-OS resolves at runtime. It mirrors the contract described in [`docs/agentos_ai_registry.md`](../docs/agentos_ai_registry.md) and is consumed by the gateway, console, control plane, and installers.

## Layout

- `REGISTRY.yaml`  top-level catalog index read by automation and installers.
- `registry.lock.json`  integrity hashes for reproducible deployments.
- `models/`, `algorithms/`, `services/`  categorized manifests with fields such as `requiresApiKey`, `integrity`, and `auto_update`.
- `scripts/`  utilities for catalog maintenance and installation (`update_catalog.py`, `install_model.py`, `install_service.py`).
- `config/`  policy configuration for updates and installer defaults.
- `security/`  minisign public keys and integrity material.
- `.github/workflows/`  scheduled workflow that refreshes the registry (`update-registry.yml`).

## Usage

- Reference registry entries as `model://<name>` or `service://<name>` in configuration and agent recipes; the gateway resolves them using [`ai_registry/REGISTRY.yaml`](REGISTRY.yaml).
- Run `python ai_registry/scripts/update_catalog.py` to regenerate `registry.lock.json` and normalize manifests when metadata changes.
- For manual installs, use `python ai_registry/scripts/install_model.py --name <id>` or `install_service.py` to fetch artifacts declared in manifests.
- CI refresh is handled by `.github/workflows/update-registry.yml`, which runs `update_catalog.py` and commits lockfile changes.

---

##  

#    Agent-OS

            AION-OS       .      [`docs/agentos_ai_registry.md`](../docs/agentos_ai_registry.md)             .

## 

- `REGISTRY.yaml`            .
- `registry.lock.json`       .
- `models/` `algorithms/` `services/`       `requiresApiKey` `integrity`  `auto_update`.
- `scripts/`       (`update_catalog.py` `install_model.py` `install_service.py`).
- `config/`        .
- `security/`    minisign   .
- `.github/workflows/`         (`update-registry.yml`).

##  

-     `model://<name>`  `service://<name>`              [`ai_registry/REGISTRY.yaml`](REGISTRY.yaml)  .
-   `registry.lock.json`       `python ai_registry/scripts/update_catalog.py`   .
-     `python ai_registry/scripts/install_model.py --name <id>`  `install_service.py`        .
-  CI  `.github/workflows/update-registry.yml`    `update_catalog.py`         .
