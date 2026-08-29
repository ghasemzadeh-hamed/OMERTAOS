# Upgrade notes

**Document role:** compatibility notes for the canonical architecture. These
notes identify required migration direction; they do not assert that every
Runtime isolation or deployment-acceptance gate is complete.

## Control/Runtime boundary

The canonical architecture uses:

- Python Control orchestration and policy layers.
- Rust runtime daemon for OS-boundary execution.

### Breaking expectations

- Direct Python process execution paths are deprecated in favor of Runtime RPC
  delegation.
- Isolation and resource operations are routed through the Runtime client and
  Runtime Daemon.

### Required components

- `runtime-daemon` binary/service;
- canonical `schemas/v1/protos/runtime.proto` contract compatibility;
- `control/clients/runtime/` client package with a configured endpoint.

The `lite`/`personal` profile supports the current allowlisted prototype
dispatch. Stronger isolation profiles still fail closed until their Linux
sandbox backends are complete.

## Docker Quickstart

- Use `deploy/docker/compose/quickstart.yml` as the canonical local stack.
- Set `CONSOLE_ADMIN_EMAIL` and `CONSOLE_ADMIN_PASSWORD` before rendering or
  starting Compose; `dev.env` contains local placeholders only.
- Runtime is now a first-class service and binds gRPC to loopback port `50051`
  by default. Control waits for its healthcheck before starting.
- The one-shot Console installer applies migrations and bootstrap data before
  dependent services proceed.

Render the resolved model before starting containers:

```bash
docker compose --project-directory . \
  -f deploy/docker/compose/quickstart.yml config
```

## Console toolchain

Console uses Next.js 15 and pnpm 11. Install with the pinned package manager:

```bash
corepack enable
corepack prepare pnpm@11.13.1 --activate
pnpm --dir console install --frozen-lockfile
```

## Windows Agentic Bridge

- Use `integrations/windows-agentic-bridge/` as the only Bridge build and
  operator path; the former compatibility mirror was retired in S5.
- Set `OMERTA_GATEWAY_URL` to the Gateway endpoint. The local default is now
  `http://localhost:8080`.
- Remove `OMERTA_CONTROL_URL`; Bridge health and task traffic now pass through
  Gateway and never connect directly to Control.
- Reinstall the Bridge Server/UI dependencies after updating. The Server now
  uses official stable v1 `@modelcontextprotocol/sdk` and the UI declares its
  Vite React plugin explicitly.
