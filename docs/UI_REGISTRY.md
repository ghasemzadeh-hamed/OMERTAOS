# UI Registry

The Local Web Dashboard (Next.js console) and the native TUI consume a single registry stored under `packages/ui-core/registry`. Navigation, dashboard widgets, and endpoint references are declared once and rendered by both UIs.

## Files
- `navigation.json` – routes, labels, and RBAC/feature flags
- `capabilities.json` – endpoint references and feature flags
- `pages/dashboard.page.json` – dashboard widget + quick-link layout
- `registry.schema.json` – shape enforced by `tools/registry_validate.py`

## Usage
- Web console: `console/lib/ui-registry.ts` imports the registry to render `/`.
- Native TUI: `console/tui/registry_loader.py` reads the same JSON and prints navigation/widgets on launch.

## Adding an item
1. Update the JSON files under `packages/ui-core/registry`.
2. Run `python tools/registry_validate.py` to enforce the schema.
3. Commit both the registry change and validation.
