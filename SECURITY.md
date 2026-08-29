# Security policy

OMERTAOS is a research prototype. Security boundaries and fail-closed behavior
are active research concerns, but the project is not security-certified,
formally verified, penetration-test certified, or approved for production use.

## Supported code

| Branch or release                     | Status                                                         |
| ------------------------------------- | -------------------------------------------------------------- |
| `CAPO` at its current HEAD            | Active research and maintenance branch                         |
| Tagged releases                       | Supported only when explicitly identified in the release notes |
| Other branches and historical commits | Best-effort only                                               |

A branch is mutable. Vulnerability reports and research results should identify
the exact affected commit.

## Report a vulnerability

Use
[GitHub Private Vulnerability Reporting](https://github.com/Hamedghz/OMERTAOS/security/advisories/new)
when available. Do not disclose exploitable details in a public issue,
discussion, or pull request.

Include:

- affected commit, component, and deployment mode;
- prerequisites and minimal reproduction steps;
- expected and observed behavior;
- confidentiality, integrity, availability, and tenant-isolation impact;
- proof-of-concept material with secrets and personal data removed;
- suggested mitigation, if known.

Maintainers will acknowledge and triage reports on a best-effort basis. A
remediation or disclosure date depends on severity, reproducibility, affected
users, and patch complexity; this document does not promise a fixed service
level.

## Current high-impact limitations

- The `lite`/`personal` Runtime path executes one allowlisted prototype intent
  without a completed Linux sandbox. Namespace, mount, seccomp, and isolated
  process backends for stronger profiles remain unimplemented and fail closed.
- Runtime named-capability and tenant-context checks exist, but signed-grant
  validation is not a complete production capability protocol.
- A local development Quickstart has been exercised; native Linux/systemd and
  production deployment acceptance remain separate, incomplete gates.
- Tenant/capability-aware Runtime node scheduling exists as a prototype;
  distributed membership and federation are not production implementations.
- Development Compose examples contain placeholder credentials and disabled
  authentication modes that must never be exposed publicly.

See the [claim ledger](docs/research/evidence-and-claims.md) for the current
evidence boundary.

## Security expectations

- keep Gateway as the only external API boundary;
- prevent Console-to-Control/Runtime and Control-to-host bypasses;
- use explicit TLS/mTLS, CORS, authentication, and secret-provider settings in
  non-development environments;
- use unique, rotated credentials; never commit tokens or private keys;
- enforce tenant and authorization context at every data and execution
  boundary;
- redact secrets and sensitive prompts from logs, traces, tests, and reports;
- pin and review dependencies, images, generated artifacts, and SBOM output;
- test negative paths, replay, expiry, cancellation, cleanup, and resource
  limits on a compatible isolated host.

## Non-security issues

Use normal GitHub issues for documentation errors, feature requests, and bugs
without a confidentiality or exploitability concern.
