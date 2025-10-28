# 🧠 Agent-OS AI Registry (Dynamic Self-Updating Repository)

**Version:** v1.0.0  
**License:** MIT  
**Language:** English  
**Author:** Hatef Project / Agent-OS Core Initiative

---

## 1. Overview

Agent-OS AI Registry is a modular, self-updating repository containing all models, algorithms, and services that AI Agents can use. It is designed for offline-safe, admin-approved, and container-free environments, while maintaining open interoperability with LLM providers and local AI stacks.

---

## 2. Key Features

| Feature | Description |
| --- | --- |
| 🧩 Universal Catalog | Unified metadata for models, algorithms, and services. |
| 🔁 Self-Updating Registry | Can automatically update from remote sources (GitHub, HuggingFace, etc.) if approved by the admin. |
| 🔐 Admin Crew Control | Updates and installations require explicit admin approval. |
| ⚙️ Installer Scripts | Each item includes install commands and integrity checks. |
| 🔒 Security & Integrity | SHA-256 verification, minisign signatures, and SBOM tracking. |
| 🚫 No Docker Required | Works with Python/Rust subprocess runners or WASM sandboxes. |
| 🌍 Offline-First Mode | Updates only when network access is granted. |
| 🧠 Agent-OS Compatible | Plugs into AION-OS / Agent-OS Control Plane for runtime orchestration. |

---

## 3. Repository Structure

```
ai-registry/
├─ REGISTRY.yaml
├─ models/
│  ├─ openai/gpt-4.5.yaml
│  ├─ google/gemini-2.5-pro.yaml
│  ├─ meta/llama-4-maverick.yaml
│  ├─ deepseek/deepseek-v3.yaml
│  └─ alibaba/qwen-2.5-max.yaml
├─ algorithms/
│  ├─ planning/react.yaml
│  ├─ rag/rag-lite.yaml
│  ├─ tot/tree-of-thought.yaml
│  └─ memory/vector-cache.yaml
├─ services/
│  ├─ vector/qdrant.yaml
│  ├─ workflow/n8n.yaml
│  ├─ database/mongodb.yaml
│  └─ storage/minio.yaml
├─ scripts/
│  ├─ update_catalog.py
│  ├─ install_model.py
│  └─ install_service.py
├─ config/
│  ├─ registry.conf
│  └─ policies.yaml
└─ .github/workflows/
   └─ update-registry.yml
```

---

## 4. Metadata Schema Examples

### 4.1 Model Manifest

```
kind: model
name: gemini-2.5-pro
provider: google-deepmind
version: "2.5.0"
release_date: "2025-07-14"
modality: [text, image, code]
license: proprietary
access: api_key
description: >
  Multi-modal reasoning model with 1M-token context and advanced plug-in support.
download:
  url: "https://ai.google.dev/models/gemini-2.5-pro"
  method: api
  install_script: "scripts/install_model.py --model gemini-2.5-pro"
integrity:
  sha256: "e3b0c44298fc1..."
  signature: "minisign:XYZ..."
resources:
  vram_gb: 16
  context_tokens: 1048576
configurable: true
compat:
  agent_api: ">=1.2"
auto_update: true
admin_approval_required: true
```

### 4.2 Algorithm Manifest

```
kind: algorithm
name: react-planner
type: planning
entrypoint: "algorithms/planning/react/runner.py:plan"
inputs: [prompt, tools[], max_steps]
outputs: [final_answer, trace[]]
depends_on:
  - model://llama-3.1-8b-instruct
  - tool://web-search
compat:
  agent_api: "^1.2"
policies:
  safety: ["no-PII-leak"]
version: "1.1.0"
integrity:
  sha256: "..."
```

### 4.3 Service Manifest

```
kind: service
name: n8n
category: workflow
version: "1.80.0"
license: AGPL-3.0
provider: n8n.io
description: >
  Open-source workflow automation service for connecting APIs and AI modules.
download:
  url: "https://github.com/n8n-io/n8n/releases/download/v1.80.0/n8n.zip"
  method: direct
  install_script: "scripts/install_service.py --service n8n"
integrity:
  sha256: "fae1c95e..."
compat:
  os: ["linux", "windows"]
  python: [">=3.10"]
configurable: true
auto_update: true
admin_approval_required: true
```

---

## 5. Registry Index File

`REGISTRY.yaml`

```
registry_version: "1.0"
catalog:
  models:
    - models/google/gemini-2.5-pro.yaml
    - models/openai/gpt-4.5.yaml
    - models/meta/llama-4-maverick.yaml
  algorithms:
    - algorithms/planning/react.yaml
    - algorithms/memory/rag-lite.yaml
  services:
    - services/workflow/n8n.yaml
    - services/vector/qdrant.yaml
installed:
  models:
    gemini-2.5-pro: /opt/ai-models/gemini-2.5-pro
    gpt-4.5: /opt/ai-models/gpt-4.5
signing:
  method: minisign
  public_key: security/publickey.txt
```

---

## 6. Policy Configuration

`config/policies.yaml`

```
update_policy:
  require_admin: true
  check_interval_hours: 24
  auto_download: false
  notify_admin_email: "admin@aionos.local"
install_policy:
  verify_signature: true
  sandbox_execution: true
  allow_external_sources: false
```

---

## 7. Installer Script Example

`scripts/install_model.py`

```python
import os, requests, hashlib, subprocess, sys, yaml

def verify_hash(path, expected):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest() == expected

def install_model(model_name):
    manifest = yaml.safe_load(open(f"models/{model_name}.yaml"))
    url = manifest["download"]["url"]
    sha = manifest["integrity"]["sha256"]
    fname = f"/tmp/{model_name}.pkg"

    print(f"📦 Downloading {model_name} from {url} ...")
    r = requests.get(url)
    open(fname, "wb").write(r.content)

    if not verify_hash(fname, sha):
        print("❌ Integrity check failed!")
        sys.exit(1)

    print("✅ Verified. Installing...")
    subprocess.run(["bash", "-c", f"tar -xf {fname} -C /opt/ai-models/{model_name}"], check=True)
    print(f"✅ {model_name} installed successfully!")

if __name__ == "__main__":
    install_model(sys.argv[1])
```

---

## 8. GitHub Workflow (Auto-Update)

`.github/workflows/update-registry.yml`

```
name: Update AI Registry
on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install pyyaml requests
      - name: Run registry updater
        run: python scripts/update_catalog.py
      - name: Commit & PR changes
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: "auto: registry update"
          title: "Auto-update AI registry"
          body: "Periodic registry refresh from external sources"
```

---

## 9. CLI Usage

```
# List available models
agentos registry list --type model

# Install a model (with admin confirmation)
agentos registry install gemini-2.5-pro

# Update registry (requires approval)
agentos registry update --approve
```

---

## 10. Example External Sources

| Provider | Registry / Endpoint | Notes |
| --- | --- | --- |
| OpenAI | https://api.openai.com/v1/models | GPT-series |
| Google | https://ai.google.dev/models | Gemini & Gemma |
| Meta | https://huggingface.co/meta-llama | Llama family |
| Alibaba | https://modelscope.cn/models/qwen | Qwen series |
| DeepSeek | https://huggingface.co/deepseek-ai | DeepSeek models |
| Mistral | https://huggingface.co/mistralai | Mistral series |
| Ollama | https://ollama.com/library | Local LLM hosting |
| HuggingFace | https://huggingface.co/models | Community registry |

---

## 11. Security & Integrity

- Minisign signatures for manifests and tarballs.
- SBOM (CycloneDX) generated per package.
- Versioned lockfile (registry.lock.json) for reproducibility.
- Sandboxed installation (ulimit / cgroups / user isolation).

---

## 12. Future Enhancements

| Feature | Description |
| --- | --- |
| 🌐 Crew AI Updater | Internal agent managing version checks & changelogs. |
| 🧱 Plugin Builder | Auto-compiles wrappers for new APIs or WASM tools. |
| 🧠 Memory Layer Integration | Syncs model metadata with Agent-OS memory graph. |
| 🔄 Version Diff Tool | Compares manifests and highlights differences. |
| 🧩 Local Cache Proxy | Mirrors remote models for air-gapped deployments. |

---

## 13. Contribution Workflow

1. Fork the repository.
2. Add or update manifests under `/models`, `/algorithms`, or `/services`.
3. Run:

   ```bash
   python scripts/update_catalog.py --validate
   ```

4. Commit and open a Pull Request:

   ```bash
   git add .
   git commit -m "Add: new model/algorithm/service"
   git push origin feature/new-entry
   gh pr create --title "New AI Model Manifest" --body "Added new entry for registry"
   ```

---

## 14. Credits

This structure merges ideas from:

- Agent-OS / AION-OS Core Blueprints
- FastAPI Control Plane (for registry API)
- Rust Data-Plane modules
- OpenAI, HuggingFace, and Mistral public registries

---

✅ **Ready for GitHub**

You can directly:

- Create a repo named `agentos-ai-registry`
- Paste this file as `/README.md`
- Push the directory tree & manifests
- Enable the included GitHub Action (`update-registry.yml`)
- Test with:

  ```bash
  python scripts/install_model.py gemini-2.5-pro
  ```

---
