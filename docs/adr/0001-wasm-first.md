# ADR 0001: WASM-First Modules

## Context

Modules must execute in diverse environments with strict sandboxing.

## Decision

Adopt WASM (WASI) as the default runtime for modules. Provide subprocess fallbacks when native libraries (GPU, OCR) are required.

## Consequences

- Requires module manifests to declare WASI compatibility.
- Enables deterministic execution and portability across hosts.
