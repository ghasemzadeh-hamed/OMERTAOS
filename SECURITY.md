# Security Policy

## Reporting a Vulnerability

Email ghasemzadeh.it@gmail.com with details and reproduction steps. Encrypt messages using the PGP key published.

## Supported Versions

| Version | Supported |
|---------|-----------|
| main | ✅ |

## Hardening Guidelines

- Enable mTLS between gateway and control plane.
- Rotate API keys and JWT signing keys every 90 days.
- Require Cosign verification before deploying module artifacts.
