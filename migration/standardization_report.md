# Full Architecture Standardization Report

## Scope
- Full repository scan (Python, Rust, frontend, config, deploy, registry).
- Multi-language dependency graphs generated.
- Cross-layer rules evaluated against canonical architecture.

## Key Metrics
- Python modules: 385
- Python edges: 365
- Python coupling score: 0.948
- Circular import groups: 0
- Max dependency depth: 7
- Rust crates: 4
- Frontend projects: 10
- Cross-layer violations: 0

## Top 10 Centrality (Python)
- module=os; centrality=58 (in=58, out=0)
- module=os.control.os.http; centrality=25 (in=5, out=20)
- module=os.control.os.core.state; centrality=17 (in=14, out=3)
- module=os.control.os.api_mod.security; centrality=15 (in=14, out=1)
- module=process-analytics.api_mod.context; centrality=13 (in=0, out=13)
- module=os.control.os.config; centrality=12 (in=10, out=2)
- module=os.control.os.api_mod; centrality=12 (in=3, out=9)
- module=os.control.os.core.deps; centrality=12 (in=11, out=1)
- module=os.control.os.routes; centrality=11 (in=1, out=10)
- module=config; centrality=8 (in=7, out=1)

## Smells
- Env scattered access points: 318
- Direct registry read patterns: 14
- Duplicated schema filenames: 0

## Orphan directories
- .claude
- .github
- aionos_core.egg-info
- ci
- config-schemas
- explorer
- gateway
- migration
- policies
- protos
- templates

## Safe refactoring actions
- No destructive bulk move executed.
- Existing deploy-oriented setup relocation retained as compatibility-preserving standardization step.

## Artifacts
- migration/repo_inventory_full.json
- migration/dependency_graph_python_full.json
- migration/dependency_graph_rust_full.json
- migration/dependency_graph_frontend_full.json
- migration/cross_layer_violations_full.json
- migration/metrics_full_after.json
- migration/migration_plan_derived.json
