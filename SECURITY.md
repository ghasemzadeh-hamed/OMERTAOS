# Security Policy

We take the security of aionOS seriously. This document explains **supported versions**, **how to report vulnerabilities**, and **how we handle disclosures**.

## Supported Versions
We actively maintain the `AIONOS` branch and the latest tagged releases.

| Version / Branch | Supported | Notes                       |
|------------------|----------:|-----------------------------|
| `AIONOS` (HEAD)  | ✅        | Active development          |
| Latest release   | ✅        | Receives fixes as needed    |
| Older releases   | ❌        | Please upgrade              |

## Reporting a Vulnerability
- Use **GitHub Private Vulnerability Reporting / Security Advisories** for confidential reports.
- If that’s not available, contact the maintainers privately (avoid public issues/PRs for security topics).
- Include:
  - Affected component(s) and version/commit
  - Reproduction steps and PoC (if any)
  - Impact assessment (confidentiality/integrity/availability)
  - Suggested fixes or mitigations (optional)

## Disclosure Process & Timelines
- **Acknowledgement:** within 3 business days.
- **Triage:** severity and scope assessed.
- **Fix:** we aim to provide a remediation plan or patch within **14 days** for high-severity issues (timeline may vary by complexity).
- **Advisory:** after a fix is available and users have reasonable time to update, we may publish a security advisory with credits (if desired).

## Hardening Guidelines
- Run Gateway/Control behind TLS; restrict management endpoints.
- Use strong API keys or SSO/OIDC in production; enforce `TENANCY_MODE` where appropriate.
- Isolate modules; prefer WASM or locked-down subprocess profiles.
- Store secrets in a vault, not `.env` committed to git.
- Enable rate limiting and idempotency to reduce abuse surface.
- Keep dependencies up-to-date; rely on CI scans (Dependabot, CodeQL/SAST if configured).
- Consider Cosign signatures & SBOMs for modules/releases.

## Non-Security Bugs
Please file normal bugs via GitHub Issues. Only use this channel for **security** concerns.
