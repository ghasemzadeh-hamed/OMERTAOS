# Security Overview

## RBAC and ABAC

- Roles: `admin`, `manager`, `user`
- Policies enforce role-based access at the gateway and control plane.
- Attribute rules check intent privacy, provider allowlists, and tenant boundaries.

## Authentication

- API keys stored in secrets manager; hashed at rest.
- JWT support with RS256 signatures; JWKS endpoints pluggable.
- Optional OIDC integration can be enabled via reverse proxy.
- Public gRPC endpoints require JWT metadata and mTLS in production (client certificates issued per tenant).

## Module Sandbox

- WASM modules run via WASI; no filesystem or network access by default.
- Subprocess modules execute under non-root user with read-only filesystem.
- Seccomp/AppArmor profiles stored under `modules/policies` (documented in manifests).

## Network Policies

- Kubernetes NetworkPolicy denies outbound traffic except HTTPS.
- Service mesh enforces mutual TLS between gateway, control plane, and module hosts. Certificates rotate automatically via SPIRE or cert-manager.

## Supply Chain

- Images signed with Cosign; verification enforced in CI using `scripts/cosign-verify.sh`.
- SBOMs generated with Syft and scanned via Trivy/Grype in GitHub Actions.
- OCI/ORAS registries store module artifacts with digest pinning.

## Secrets Handling

- Use Kubernetes Secrets or HashiCorp Vault for provider credentials.
- Modules declare required secrets in manifest `permissions.secrets`.
- Control plane masks PII in logs and structured metrics.

## Compliance

- Audit activity written to Kafka topic `aion.audit.activity`.
- Log retention configurable per environment (dev 7-14 days, prod 30-90 days).
- Kernel proposals require explicit approval from an administrator or a signed inbound webhook. Every applied change carries TTL,
  canary scope, and rollback metadata managed by SAFEKEEPER. Inbound webhooks validate HMAC signatures (`AION_INBOUND_WEBHOOK_SECRET`)
  and restrict commands via `policies/webhooks.yaml`.
