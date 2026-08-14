# S3.7 migration — Integrations consolidation

Date: 2026-07-15

Status: `integrations/windows-agentic-bridge/` is the canonical Windows Bridge;
the matching `execution/` tree is a protected compatibility mirror until S5.

## Impact analysis

- Both Bridge trees contained the same 39 relative files. Thirty-eight were
  byte-identical; only their root README files differed.
- No unique or newer source, manifest, UI, script, test or configuration asset
  required migration from `execution/`.
- Console, WSL scripts, ODR manifest and operator documentation already point to
  `integrations/windows-agentic-bridge/`.
- The audit found and removed a direct Bridge-to-Control health connection.
  Bridge network calls now cross Gateway only, and Gateway reports downstream
  Control health through its normal health response.
- Task submission/status now use the existing versioned Gateway routes.
- The unavailable `@microsoft/ai-mcp-sdk` prototype dependency was replaced by
  the official stable v1 `@modelcontextprotocol/sdk`; low-level stdio handlers
  preserve JSON Schema tool descriptions and validate inputs with declared Ajv.
- The missing Vite React plugin is now declared explicitly for the Bridge UI.
- Database objects, OMERTAOS auth implementation, core public APIs, Runtime,
  deployment topology and dependencies are unchanged.
- Risk is high because this integration handles an administrative token and
  exposes MCP tools to an external host.

## Canonical ownership and compatibility

`integrations/windows-agentic-bridge/` is the only development and operator
entrypoint. `execution/windows-agentic-bridge/` remains byte-identical for every
file except its compatibility README. An architecture test rejects unique files
or source drift so fixes cannot silently land in only one copy during the
protected window.

No file was deleted. The mirror exists for rollback and retirement evidence,
not as a second implementation. Permanent deletion remains an S5 action.

## Boundary and security changes

- `OMERTA_CONTROL_URL` and the Control URL UI field were removed.
- The default Gateway endpoint is `http://localhost:8080`, matching the active
  root/Quickstart Gateway port rather than the Console port.
- `OmertaClient` creates one HTTP client and uses Gateway health plus versioned
  `/v1/tasks` routes.
- The health tool keeps its `gateway` and `control` result keys; `control` is now
  derived from Gateway's dependency status rather than a forbidden direct call.
- Tokens remain environment-only and are not written into the ODR manifest,
  source, UI state persistence or logs.
- MCP diagnostics use stderr only so logs cannot corrupt the stdout JSON-RPC
  transport.

Agent Catalog Gateway routes do not exist in the current canonical Gateway.
S3.7 does not reconstruct that feature; `list_agents` and `get_agent` remain a
documented runtime limitation rather than permission to call Control directly.
Placeholder admin and memory tools were not expanded or granted capabilities.

## Validation

```powershell
python -m pytest tests/architecture/test_integration_consolidation.py -q
python -m pytest tests/architecture tests/control -q -k "not test_structure_migration_gate"
npm run build --prefix integrations/windows-agentic-bridge/bridge-server
npm run test --prefix integrations/windows-agentic-bridge/bridge-server -- --run
npm run build --prefix integrations/windows-agentic-bridge/bridge-ui
```

Dependencies are installed from the reviewed manifests without generating
lockfiles because neither Bridge package previously committed one. Reproducible
lockfiles remain required before production release. Windows/WSL/ODR runtime
acceptance remains pending on the intended host.

The repaired toolchain validation passed: Bridge Server TypeScript build,
2 Vitest files/3 tests and Bridge UI production build. The UI build transformed
40 modules. No dependency lockfile was generated.

## Migration and rollback

Operators should use only the canonical integration path and remove
`OMERTA_CONTROL_URL` from local Bridge configuration. No data migration is
required. Existing task and health tool names remain unchanged.

Rollback restores the previous Bridge configuration/client behavior and both
mirrored source copies together. Do not restore a direct Control connection in
production; use the pre-S3.7 state only for code recovery. Do not delete either
tree without explicit S5 approval and green Windows/WSL acceptance evidence.
