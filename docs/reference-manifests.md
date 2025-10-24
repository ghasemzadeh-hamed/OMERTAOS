# Reference Manifests & Configurations

## 1. Intent Registry (`intents.yml`)
```yaml
summarize:
  default_route: auto
  candidates: [local, api, hybrid]
  privacy: allow-api
  tiers_allowed: [tier0, tier1]
  vector_usage: false

invoice_ocr:
  default_route: hybrid
  candidates: [local, hybrid]
  privacy: local-only
  tiers_allowed: [tier0]
  vector_usage: true
```

## 2. Policy Pack (`policies.yml`)
```yaml
budget:
  default_usd: 0.02
  hard_cap_usd: 0.20
latency:
  p95_ms:
    local: 600
    api: 2000
    hybrid: 2300
privacy:
  local_only_intents: ["invoice_ocr"]
providers:
  deny: []
  allow: ["ollama", "openai", "azure", "hf", "vllm"]
routing:
  fallback_order: ["local", "api", "hybrid"]
```

## 3. Model Catalog (`models.yml`)
```yaml
tiers:
  tier0:
    local: ["ollama:qwen2.5", "vllm:llama3.1"]
  tier1:
    cloud: ["openai:gpt-4.1-mini", "azure:gpt-4o-mini", "hf:mistral-large"]
  tier2:
    cloud: ["openai:gpt-4.1", "azure:gpt-4o", "hf:mixtral-8x22b"]
```

## 4. Module Registry (`modules.yml`)
```yaml
modules:
  - name: summarize_text
    ref: "ghcr.io/aion/summarize_text:1.3.0"
    runtime: wasm
    signatures: ["cosign:..."]
    timeout_ms: 1500
    limits: { cpu: "0.5", memory: "256Mi" }
```

## 5. AIP Package Manifest
```yaml
apiVersion: aionos/v1
kind: AgentPackage
metadata:
  name: summarize_text
  version: "1.3.0"
  authors: ["AION Core"]
  license: Apache-2.0
  signatures:
    cosign: "sigstore://ghcr.io/aion/summarize_text@sha256:..."
  sbom: "oci://ghcr.io/aion/sbom/summarize_text:1.3.0"
runtime:
  type: wasm
  wasi: true
  resources:
    cpu: "0.5"
    memory: "256Mi"
    gpu:
      required: false
      vendor: none
permissions:
  filesystem: read-only
  network: deny
  secrets: ["OPENAI_API_KEY?"]
entrypoints:
  grpc:
    port: 0
  schema:
    input: "schemas/summarize_input.json"
    output: "schemas/summarize_output.json"
intents:
  - "summarize"
policies:
  timeout_ms: 1500
  retries: 0
```

## 6. Rate Limit Configuration (`ratelimit.yml`)
```yaml
api_keys:
  default:
    rate_per_minute: 60
    burst: 120
ips:
  default:
    rate_per_minute: 120
    burst: 200
```

## 7. Kafka Topic Schema Registry Entries
```yaml
subject: aion.router.decisions-value
version: 1
schema:
  type: record
  name: RouterDecision
  namespace: aion
  fields:
    - { name: task_id, type: string }
    - { name: intent, type: string }
    - { name: route, type: string }
    - { name: tier, type: string }
    - { name: reason, type: string }
    - { name: timestamp, type: long }
```

## 8. Grafana Dashboard Checklist
- Router Overview: route distribution, tier cost, p95 latency.
- Task Health: queue depth, retry rate, failure heatmap.
- Resource Utilization: CPU/RAM/GPU per module, Kafka consumer lag.
- Security Overview: auth failures, rate-limit hits, policy overrides.

## 9. SBOM & Signing Pipeline
1. Generate SBOM via `syft dir:./module -o cyclonedx-json`.
2. Attach SBOM artifact to OCI registry using ORAS (`oras attach`).
3. Sign module with cosign: `cosign sign ghcr.io/aion/summarize_text:1.3.0`.
4. Verify signature during install: `cosign verify ghcr.io/aion/summarize_text:1.3.0`.
