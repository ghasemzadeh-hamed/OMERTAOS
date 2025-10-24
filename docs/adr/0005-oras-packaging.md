# ADR 0005: ORAS Packaging for Modules

## Context

Modules and policies must be distributable without Docker dependencies.

## Decision

Publish modules as OCI artifacts using ORAS. Include Cosign signatures and SBOMs in the registry metadata.

## Consequences

- Requires CI to push to an OCI registry with `oras` tooling.
- Module host must authenticate to registry and validate signatures before execution.
