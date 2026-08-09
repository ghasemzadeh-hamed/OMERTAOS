# Project governance

OMERTAOS is maintained as an open research and engineering project. Repository
access or contribution does not by itself authorize publication claims,
production deployment, or changes to security-sensitive boundaries.

## Roles

- **Maintainers** review changes, manage releases and advisories, and protect
  repository integrity.
- **Component reviewers** provide focused review for Console, Gateway, Control,
  Runtime, data, schemas, deployment, or research evidence.
- **Contributors** propose changes through issues and pull requests.
- **Research reviewers** assess methodology, evidence, limitations, and
  manuscript consistency; they do not replace code or security review.

Current authority is determined by repository permissions and reviewed pull
requests, not by role titles listed in a document.

## Decisions

- routine, backward-compatible changes use normal pull-request review;
- architecture, trust-boundary, public-contract, schema, or deployment-topology
  changes require an ADR and review from affected owners;
- security vulnerabilities follow the private process in
  [SECURITY.md](SECURITY.md);
- disputed technical decisions should record alternatives, evidence, risks,
  and a reversible path rather than relying on undocumented consensus.

## Evidence and publication

Performance and security results must identify the exact commit, environment,
method, raw artifacts, exclusions, and limitations. Manuscript submission or
public release requires author approval and an independent consistency check
against [Evidence and claims](docs/research/evidence-and-claims.md).

The repository does not imply that a draft manuscript is accepted, that every
listed feature is implemented, or that CI constitutes certification.

## Releases

Releases are made when a reviewed scope and validation record are available;
there is no guaranteed calendar. Release notes should include compatibility,
migration, security, rollback, known limitations, and the immutable commit or
tag.

## Amendments

Governance changes are proposed by pull request and should explain why the
change is needed, who is affected, and how ongoing work remains reviewable.
