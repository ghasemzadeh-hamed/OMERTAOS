# POLICIES

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Policy Bundles
Policy assets define security, routing, and governance constraints for kernel and control layers.

## Enforcement Points
- Control-plane authorization
- Kernel action validation
- Registry/model usage constraints

## Governance Model
- Policy-as-code with versioned artifacts
- Auditability through deployment bundles and changelogs
