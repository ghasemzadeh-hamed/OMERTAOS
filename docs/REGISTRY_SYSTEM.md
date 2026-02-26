# REGISTRY_SYSTEM

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Canonical Metadata Source
Registry artifacts define:
- model descriptors
- algorithm descriptors
- service manifests
- lock metadata

## Model Resolution
- Resolver maps aliases/IDs to concrete model entries.
- Control and runtime layers consume resolved metadata only.

## Version Locking
- `registry.lock.json` supports deterministic rollouts.
- Lock snapshots are auditable deployment evidence.

## Hosted Model Resolver
- Hosted backends (e.g., cloud/API providers) are selected by policy + routing metadata.
- Resolver enforces stable schema between registry and control-plane consumers.
