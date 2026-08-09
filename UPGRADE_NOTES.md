# Upgrade Notes

**Document role:** compatibility notes for the canonical architecture. These
notes identify required migration direction; they do not assert that every
Runtime isolation or deployment-acceptance gate is complete.

## Hybrid Runtime Migration

The canonical architecture uses:

- Python Control orchestration and policy layers.
- Rust runtime daemon for OS-boundary execution.

### Breaking expectations

- Direct Python process execution paths are deprecated in favor of runtime daemon RPC delegation.
- Isolation/resource operations are routed through runtime client and runtime daemon.

### Required components

- `runtime-daemon` binary/service
- canonical `schemas/v1/protos/runtime.proto` contract compatibility
- `control/clients/runtime.py` configured endpoint

## Windows Agentic Bridge configuration

- Use `integrations/windows-agentic-bridge/` as the only Bridge build and
  operator path; the former compatibility mirror was retired in S5.
- Set `OMERTA_GATEWAY_URL` to the Gateway endpoint. The local default is now
  `http://localhost:8080`.
- Remove `OMERTA_CONTROL_URL`; Bridge health and task traffic now pass through
  Gateway and never connect directly to Control.
- Reinstall the Bridge Server/UI dependencies after updating. The Server now
  uses official stable v1 `@modelcontextprotocol/sdk` and the UI declares its
  Vite React plugin explicitly.
