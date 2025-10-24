# Security Notes

- **Authentication**: Gateway issues JWTs; control plane verifies tokens before privileged actions. NextAuth handles OAuth and credential sign-in with bcrypt hashing.
- **Rate Limiting**: Gateway enforces 100 req/min per client via `@fastify/rate-limit`.
- **RBAC**: Control plane restricts management routes to `admin`/`manager` roles through dependency guards.
- **Sandbox Execution**: Rust execution plane is isolated behind gRPC; runtime layer provisions containerd with wasmtime for WASM workloads.
- **Transport Security**: Configure mTLS between planes via Fastify and gRPC TLS options (see `docs/performance.md` for tuning). Certificates should be provisioned via Vault in production.
- **Signed Modules**: Module manifests (`execution/modules/**/manifest.yaml`) include signing metadata for Cosign validation.
- **Audit Trail**: ActivityLog entries stored for each task lifecycle event; real-time updates broadcast via Redis channels.
- **SBOM**: Use `syft` to generate SBOM for each service container before release.
