---
name: security
description: Review or harden OMERTAOS authentication, authorization, tool access, prompt-injection defenses, runtime sandboxing, secrets, and audit behavior. Use for explicit security work.
---

# OMERTAOS Security Skill

## Execution Mode

- Review-only requests produce evidence-backed findings without edits.
- Fix/harden requests require the smallest safe patch plus targeted security and
  regression tests; do not stop at recommendations.
- Never expose secrets or weaken a control to make a test pass.

## Checklist

- Authentication and authorization
- Tenant isolation and IDOR resistance
- Prompt-injection and tool-permission guards
- Runtime sandbox/capability policy
- Secret handling, safe logs, and safe errors
- Input validation, rate limits, and audit events
- Human approval for truly destructive or production actions

Order findings as Critical, High, Medium, then Low and cite concrete evidence.
