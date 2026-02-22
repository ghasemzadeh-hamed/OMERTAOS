# OMERTAOS Architectural Analysis (Phase 1)
## Detected System Components
- **Agent runtime modules**: app/llm, process-analytics/predictive, process-analytics/prescriptive, os/kernel
- **Control plane**: control, app/control, aion/control, aionos_control
- **Registry system**: ai_registry, services/aion-model-registry, os/control/models/registry.py
- **MongoDB adapters**: services/aion-memory, aion/db
- **Rust execution sandbox**: execution, modules
- **BigData pipelines**: bigdata/pipelines, process-analytics
- **CLI entrypoints**: cli/main.py, cli/aion/cli.py, aionos_core/cli.py
- **Kernel / multi-tenant logic**: os/kernel, kernel-multitenant
- **Policy modules**: policies, os/kernel/policy_engine.py
## Graph & Risk Findings
- Python files analyzed: 376
- Rust files analyzed: 10
- API endpoints detected: 133
- Worker/background references: 9
- Circular import groups detected: 0
- Cross-layer violations detected: 0
## Specific smells
- Env var access points: 55
- Direct/implicit registry reads: 7
- Config loading scatter points: 28
## Recommendation gate
- Proceed with migration by introducing compatibility shims first; avoid hard moves before abstraction layer lands.
