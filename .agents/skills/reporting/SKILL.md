---
name: reporting
description: Implement or analyze product-facing OMERTAOS reports, dashboards, KPI views, exports, audit summaries, and model-usage reports. Do not use for engineering status reports or routine task summaries.
---

# OMERTAOS Reporting Skill

## Execution Mode

- This skill is for product reporting features and analytics, not for writing a
  Markdown completion report about engineering work.
- For implementation requests, change the relevant report/query/UI code and run
  targeted tests. Do not stop after defining a report format.
- For analysis-only requests, validate metric definitions and remain read-only.

## Rules

- Define metric meaning, grain, owner, source, and date range clearly.
- Separate operational, model, workflow, cost, latency, and audit metrics.
- Validate filters, tenant scope, totals, and empty/error states.
- Avoid misleading aggregation and support export only when in scope.

## Product Report Content

Use only the sections that help the product audience: summary, key metrics,
breakdown, risks, and recommended actions.
