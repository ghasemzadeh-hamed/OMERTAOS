# OMERTAOS / AION-OS

OMERTAOS is a modular operations platform for managing AI workloads. This repository contains the
control plane (FastAPI), gateway (Node.js), and console (Next.js) services along with supporting
modules and tooling.

## Native (No Docker) installation

Prefer to run everything directly on the host? Follow the step-by-step guide in
[`docs/INSTALL_native.md`](docs/INSTALL_native.md) for Linux and Windows instructions, automated
installers, system service management, and smoke tests.

For container-based workflows, continue using the existing Docker compose stacks under `docker-compose*.yml`.

## Model Training & CI Guard

The repository ships with an anti-overfitting training stack that can be exercised locally or in CI:

- Install dependencies and train with guard rails:
  ```bash
  make setup
  make train
  make guard
  ```
- Training reads [`policies/training.yaml`](policies/training.yaml) for split strategy, cross-validation, regularization, early stopping, ensembles, and feature-selection knobs.
- Artifacts (metrics, configuration, permutation importances) are stored under `artifacts/` to keep runs reproducible.
- The `model-check` GitHub Actions workflow mirrors this process on every push/PR using the `--ci` synthetic dataset fallback. It fails when the train/validation gap or cross-validation standard deviation exceeds policy thresholds, or when PSI drift breaks the configured guard.

Reproducibility is enforced via fixed seeds, deterministic preprocessing pipelines, and artifact logging so trained models can be audited or regenerated.
