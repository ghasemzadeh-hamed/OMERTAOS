# OMERTAOS Canonical Structure

Canonical top-level architecture:

- `core`
- `agents`
- `control`
- `registry`
- `config`
- `schemas`
- `execution`
- `db`
- `bigdata`
- `cli`
- `console`
- `kernel`
- `policies`
- `shared`
- `deploy`
- `tests`
- `tools`

Notes:
- Runtime modules should migrate toward these canonical roots using dependency-safe phases.
- Backward compatibility shims/wrappers are acceptable during transition windows.

- Legacy `os/*` modules are being distributed into `control`, `kernel`, `shared`, and `deploy` with compatibility shims.
