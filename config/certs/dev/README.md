# Development certificates

The files in this directory are generated automatically by
`scripts/generate_dev_certs.py` for local development and CI runs when Vault is
not yet available. The certificates are short-lived, self-signed and **must not
be used in production environments**.

The generator creates:

- `dev-ca.pem` / `dev-ca.key` - ad-hoc certificate authority
- `control-server-cert.pem` / `control-server-key.pem` - TLS material for the
  control service
- `gateway-client-cert.pem` / `gateway-client-key.pem` - mTLS client
  certificate used by the gateway during tests
- `.generated` - timestamp marker so tooling can detect when the bundle was last
  refreshed

Artifacts are ignored by Git via `.gitignore` to avoid committing transient
keys. Delete the directory or the `.generated` marker to force regeneration.
