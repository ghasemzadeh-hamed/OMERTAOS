# Bootstrap certificates

Files in this directory are created automatically by `scripts/quicksetup.sh`
when Vault integration is disabled. They are intentionally short-lived and must
be replaced with Vault-issued material once the platform is fully initialised.

Generated files:

- `bootstrap-ca.pem` and `bootstrap-ca-key.pem`
- `control-server.pem` and `control-server-key.pem`
- `gateway-client.pem` and `gateway-client-key.pem`
- `.generated` marker file that records the timestamp and validity window

Generated key material is excluded from version control so these sensitive
artifacts are never committed.
