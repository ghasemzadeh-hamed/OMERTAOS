# OMERTAOS Project Rules

## Task Execution Priority

- The current user request overrides historical task boards and roadmap items.
- Implementation requests must produce a focused patch and targeted validation;
  Markdown cannot substitute for the requested implementation.
- The short impact analysis is a progress update, not an approval gate.
- Create or update documentation only when behavior, API, schema/migration,
  setup/configuration, architecture contracts, or operator workflows change.
- Stay on the current branch unless the user explicitly asks to switch.

## Development Priority

1. Stabilize CAPO native setup.
2. Stabilize quickstart Docker/Compose.
3. Preserve Console -> Gateway -> Control -> Runtime Daemon.
4. Only after stability, clean duplicates and canonicalize structure.

## Native-First Rule

Native setup must not run long-running services automatically.

Allowed in setup:
- runtime checks
- dependency installation
- folder creation
- non-destructive validation

Forbidden in setup:
- docker compose up
- npm run dev
- uvicorn long-running server
- destructive cleanup
- migration execution without approval

## Docker Rule

Docker is a manual action in this phase.

Allowed:
- docker compose config
- docker compose build
- docker compose up -d only when explicitly requested
- docker compose down only when explicitly requested

Docker quickstart target ports:
- Console: 3000
- Gateway: 8080
- Control: 8000
- Runtime gRPC: 50051, optional in this phase

## Architecture Safety

- Do not bypass Gateway.
- Do not mix UI logic with Control logic.
- Do not put runtime execution logic in Console or Gateway.
- Do not move Rust runtime without explicit migration plan.
- Do not duplicate model registry sources further.
- Do not add a new source of truth for schemas/protobufs.

## Security Rules

- Never print secrets.
- Never commit real .env files.
- Never log raw passwords, tokens, sessions, cookies, API keys, or private keys.
- Never show raw database errors to users.
- Use auth and permission checks before sensitive actions.
- Validate and sanitize inputs.
- Use safe database bindings.
- Protect file-explorer, update, shell, runtime, and tool-execution features.

## Refactor Rules

- No large folder migration in the CAPO setup phase.
- Prefer compatibility wrappers over breaking imports.
- Use git mv only after reference checks.
- Before deleting anything, run:
  - git log --oneline -- <path>
  - rg '<path or import name>'
  - find . -type f | grep '<path>'

## Testing Rules

- Run syntax checks where available.
- Run pytest if Python tests exist.
- Run npm tests for console/gateway if available.
- Run docker compose config before docker compose build.
- Do not claim successful execution if commands were not run.
