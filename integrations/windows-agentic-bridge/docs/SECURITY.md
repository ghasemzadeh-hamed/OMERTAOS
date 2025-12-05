# Security considerations

## Threats
- Prompt injection via tool parameters sent to OMERTA agents
- Abuse of admin tools (restart/metrics) from untrusted MCP clients
- Leaked tokens if environment variables are logged or checked into VCS

## Mitigations
- Tools defined with strict JSON schemas; invalid inputs rejected early
- Admin tools are grouped separately so they can be toggled off in manifest or UI
- Secrets only loaded from environment or `.env` (excluded from VCS)
- Structured logging without echoing sensitive tokens
