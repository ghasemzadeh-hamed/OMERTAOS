# OMERTAOS Security Rules

## Critical Security Context

OMERTAOS may access:
- files
- tools
- models
- APIs
- runtime execution
- databases
- system-level operations

Therefore, security is a first-class architecture layer.

## Secrets

Never expose:
- API keys
- Passwords
- Tokens
- Private keys
- Session IDs
- Database credentials
- Internal server paths in public UI
- .env values

## Runtime Safety

This section governs agents executed by the OMERTAOS product. It does not block
Codex from performing non-destructive engineering commands and repository edits
that the user requested and the active Codex tool policy permits. Codex must
still request additional authority for destructive, production, secret-bearing,
or external-state operations.

- Agent cannot use file system without policy.
- Agent cannot execute shell without explicit policy and approval.
- Agent cannot access another tenant's data.
- Agent cannot show secrets in responses.
- Sensitive tool calls must be audited.
- Critical actions should require human approval.

## Gateway Security

Gateway must preserve:
- authentication
- authorization
- rate limiting
- CORS policy
- helmet/security headers
- request validation
- telemetry where available

## Data Security

- Enforce tenant isolation.
- Validate retrieval permissions.
- Do not leak document chunks across tenants.
- Do not send confidential or secret data to cloud models unless policy allows it.

## File Upload Security

- Validate file type.
- Validate file size.
- Store safely.
- Never execute uploaded files.
- Normalize extracted content before indexing.

## Audit

Sensitive actions must log:
- actor
- tenant
- action
- resource
- risk level
- timestamp
- result
