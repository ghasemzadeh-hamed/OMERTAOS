# Module Packaging and Installation

## Overview

aionOS modules are distributed as OCI artifacts signed with Cosign and accompanied by SBOM metadata. Each module includes a manifest (`manifest.yaml`) that describes runtime characteristics, intents, resource policies, and security boundaries.

## Manifest essentials

```yaml
metadata:
  name: summarize_text
  version: 1.2.0
runtime:
  type: wasm
  wasi: true
resources:
  cpu: "250m"
  memory: "512Mi"
permissions:
  fs: read-only
  net: none
intents:
  - summarize
```

## Signing and SBOM

1. Generate an SBOM using Syft: `syft packages . -o spdx-json=sbom.spdx.json`.
2. Sign the module artifact with Cosign: `cosign sign --key cosign.key ghcr.io/aionos/modules/summarize_text:1.2.0`.
3. Store the Cosign public key in secure storage and reference it during installations.

## Installation workflow

Use `scripts/install_module.sh` to fetch and verify a module from an OCI registry:

```bash
COSIGN_KEY=cosign.pub ./scripts/install_module.sh ghcr.io/aionos/modules/summarize_text:1.2.0 modules/summarize_text
```

The script performs an ORAS pull, verifies the signature, and places the manifest, SBOM, and binary artifacts under the destination folder. After installation, update `policies/modules.yml` to enable the module for routing decisions.

To publish or update a module, run:

```bash
COSIGN_KEY=cosign.key ./scripts/register_module.sh summarize_text modules/summarize_text ghcr.io/aionos/modules
```

This command pushes the artifact and signs it with Cosign for downstream verification.

## Runtime registration

Once a module is installed, the control plane automatically discovers manifests from `modules/**/manifest.yaml`. The router caches manifest metadata in Postgres with an optional `tenant_id` field to support multi-tenant scheduling. Cache invalidation occurs whenever `scripts/register_module.sh` or the policy reload endpoint is invoked.
