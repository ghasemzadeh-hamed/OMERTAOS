# Schema and Protobuf contracts

**Document role:** normative contract ownership and compatibility policy.
Generated-binding freshness and cross-version compatibility must be established
by the relevant build/test run for the evaluated commit.

`schemas/` is the source of truth for versioned service, event and configuration contracts. Generated clients are outputs and must not be edited manually.

Authored contracts live under `schemas/v1/`. Generated bindings live under
`shared/generated/{python,typescript,rust}/`; compatibility wrappers elsewhere
must only re-export those outputs. The current Python task bindings were recovered
from Git history and require fresh toolchain regeneration before release.

Protobuf defines internal gRPC APIs and core messages because it provides language-neutral contracts, compact binary encoding, generated Python/TypeScript/Rust bindings, explicit service methods, and enforceable compatibility. JSON Schema remains appropriate for public JSON, events and configuration where human readability and ecosystem tooling matter.

Core contracts include:

- `Task`: identity, tenant, actor, input/reference, constraints, lifecycle, timestamps, idempotency/correlation metadata and result/error reference.
- `Agent`: identity/version, skills, accepted task versions, entrypoint/artifact digest, model constraints, capabilities and resource bounds.
- `Model`: provider/model/version, modalities, token limits, tool support, routing attributes, regions and credential reference.
- Runtime RPCs: dispatch, cancel, heartbeat, event/result stream and capability grant envelope.

Contracts are grouped by major namespace (`omertaos.v1`). Published field numbers and enum values are never reused. Additive optional fields are preferred; removed fields/names are reserved. Changing meaning/type, required semantics, identity, or ordering guarantees requires a new major contract or parallel RPC. Consumers tolerate unknown fields and producers provide safe defaults.

CI must lint and compile every contract, compare wire compatibility against the release baseline, regenerate bindings reproducibly, and run cross-version contract tests. Event envelopes include event ID/type/version, occurred time, tenant, producer, correlation/causation IDs, trace context, payload and content type.
