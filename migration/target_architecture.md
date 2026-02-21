# Target Canonical Architecture (Phase 2)

## Canonical structure
- /core
- /agents
- /control
- /registry
- /config
- /schemas
- /execution
- /db
- /bigdata
- /cli
- /console
- /kernel
- /policies
- /shared
- /deploy
- /tests
- /tools

## Layer rules
1. Control plane must not depend on CLI.
2. CLI depends only on core + control API.
3. Registry is canonical metadata source.
4. Agents never read raw registry files directly.
5. Config only via unified loader.
6. Rust execution isolated under /execution.
7. BigData isolated from control runtime.
8. No circular cross-layer dependencies.

## Execution gate
- No circular risk detected; full dependency-safe relocation can proceed.
- This migration run focuses first on non-breaking abstraction layers and compatibility shims.
