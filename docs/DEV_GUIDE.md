# DEV_GUIDE

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Local Development
1. Clone repository
2. Configure environment files
3. Start dependencies (compose/native)
4. Run control, gateway, and console components

## Recommended Workflow
- run targeted tests by subsystem
- validate API routes and CLI behavior
- keep docs aligned with architecture changes

## Documentation-first Refactors
When changing architecture:
1. update architecture docs
2. update API/CLI references
3. validate markdown links
4. capture migration artifacts
