---
name: code-review
description: Review OMERTAOS code for bugs, regressions, security risks, and architecture violations. Use for review/audit requests; implement fixes only when the user also asks to fix them.
---

# OMERTAOS Code Review Skill

## Execution Mode

- A review-only request is read-only: report actionable findings with file and
  line evidence.
- If the user asks to fix findings, apply the smallest safe patch and run
  targeted tests in the same task.
- Do not create a review Markdown file unless explicitly requested.

## Review Checklist

- Preserves Console -> Gateway -> Control -> Runtime Daemon
- No direct Console -> Control bypass
- No runtime execution in UI/Gateway
- Syntax correctness and runtime errors
- Security, permission, and input-validation risks
- Database safety and tenant isolation
- Duplicate logic and backward compatibility
- Error handling and performance regressions

## Output Format

Lead with findings ordered by severity. Include exact file/line evidence, then
open questions and a short conclusion. Do not invent findings to fill headings.

## Suggested Fix

Include only when implementation was not requested; otherwise apply and test the
fix.
