# Cluster federation

**Status:** research direction; not implemented.

Federation would connect independently administered OMERTAOS domains without
creating a shared implicit trust zone. Each domain retains authority over its
identities, policies, data, Runtime nodes, and audit retention.

## Design questions

- how identities and policy decisions are represented across domains;
- which contracts and capability vocabularies are mutually understood;
- how data residency and artifact transfer are constrained;
- how revocation, clock skew, retries, and partial failure are handled;
- which audit evidence is shared and which remains local;
- how a remote result is attributed without trusting remote internals.

Federation should use explicit, versioned agreements and least-privilege
capabilities. It must not expose Runtime directly or allow a remote Console or
Gateway to bypass the local Control authority.

No interoperability, cross-domain security, or federated scalability claim is
made by the current repository.
