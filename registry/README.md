# Agent and model registry

**Document role:** registry ownership and target metadata model. The example is
illustrative; current supported fields and lifecycle behavior must be verified
against versioned schemas and tests.

The Registry is the versioned catalog used by Control to resolve executable agents and eligible models. It stores metadata and lifecycle state; it does not execute agents or call models.

The Model Registry describes provider/model identity, immutable version, endpoint class, modalities, context/output limits, tool support, regions, data classification, pricing, latency/quality profiles, health policy, credentials reference, and fallback compatibility. The Agent Registry describes agent identity/version, skills, accepted task schemas, planner/runtime entrypoint, required capabilities, allowed model constraints, resource bounds, artifact digest, tenant visibility, and status.

```yaml
apiVersion: omertaos.io/v1
kind: Model
metadata:
  name: example-model
  version: 1.2.0
spec:
  provider: example
  modelId: example/model
  modalities: [text]
  contextTokens: 128000
  capabilities: [tools, structured-output]
  regions: [eu-west]
  credentialRef: secret://models/example
  routing:
    costClass: medium
    latencyClass: interactive
status:
  phase: active
```

Metadata is schema-validated and committed as YAML under Registry ownership; credentials are references only. Published versions are immutable and use semantic versioning. Breaking metadata/contract changes require a major version. Lifecycle states are draft, active, deprecated, disabled, and retired; tasks pin exact versions for reproducibility.

Control requests candidates with hard constraints. Dynamic selection removes unhealthy, disabled, unauthorized, region-incompatible, over-budget, or capability-incompatible entries, then scores quality, latency, cost and load. Registry returns metadata and health snapshots; Control owns the final auditable routing decision and fallback chain.
