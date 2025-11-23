# Change & Release Management

## 1. Release Notes / Changelog
- **Template**
  - **Release ID/Date:** YYYY-MM-DD, version tag (e.g., v1.4.0).
  - **New Features:** bullet list with owner and ticket link.
  - **Improvements:** performance, usability, infra changes.
  - **Bug Fixes:** issue ID, impact, verification notes.
  - **Breaking Changes:** migration or config updates with rollback guidance.
  - **Known Issues:** workarounds and expected fix versions.
  - **Upgrade Instructions:** ordered steps, pre-checks, post-checks.
  - **Artifacts & Checksums:** download URLs, signatures, SBOM link.
- **Ownership & Timing:** Release manager compiles notes during release candidate hardening; product owner signs off before GA; notes published with tags and artifacts.
- **Communication:** Markdown changelog in Git, highlighted summary in release channel/email; console/portal banner for breaking changes.
- **Maintenance & Versioning:** `docs/CHANGELOG.md` (or release.md) updated per tag; automation encouraged via conventional commits + changelog generator; each release tagged with semver and linked changelog section.

## 2. Versioning Strategy
- **Scheme:** Semantic Versioning `MAJOR.MINOR.PATCH`; patch = hotfixes, minor = backward compatible features, major = breaking changes.
- **Branching:** Trunk-based with short-lived feature branches; release branches cut for RC stabilization; tags applied on main after green release pipeline.
- **Compatibility/Deprecation:**
  - Backward-compatible APIs retained for two minor versions with deprecation warnings and console notice.
  - Breaking changes require major bump, migration guide, and feature flags where feasible.
- **Artifacts:** Container images, installers, and manifests versioned consistently; Docker tags mirror git tags plus `latest` pointer after promotion.

## 3. Code Review & Merge Policy
- **Process:** PRs require at least one code owner and one domain reviewer (security/perf as needed). Criteria: correctness, tests, docs, security implications, and adherence to style guides.
- **Checks:** CI must pass (lint, unit, integration where applicable, SAST/DAST gates); coverage threshold enforced (e.g., >=85% statements for core services).
- **Merge Rules:** Squash-and-merge to main; release manager approves merges into release branches; no direct pushes to main. Hotfixes cherry-picked to release branch and backported to main post-validation.
- **Traceability:** Link PRs to issues/tickets; require changelog entry or justification for omission.

## 4. Rollback Plan for Each Release
- **Triggers:** Error-rate or latency breach vs SLO, failed health checks, regression in critical paths, or security incident.
- **Steps:**
  1) Halt further rollout/canary and notify incident channel.
  2) Revert to previous stable tag (redeploy containers/installer artifacts) or perform git revert for config changes.
  3) Roll back database migrations using down scripts or restore latest backup if non-reversible; disable new features via flags.
  4) Validate rollback: smoke tests, health checks, dashboards, and error budgets.
  5) Document incident, root cause, and follow-up actions; update release notes with rollback notice.
- **Targets:** Rollback decision within 15 minutes of trigger; execution completed within 30 minutes for app layer, 60 minutes for schema rollbacks when safe.

## 5. Documentation Update Policy
- **Responsibility:** Feature authors update technical docs and changelog; tech writer/release manager reviews for consistency before GA.
- **Timing:** Documentation PR merged before release cut; urgent fixes allowed post-release with clear version annotation.
- **Scope:** API references (OpenAPI/gRPC), user guides, deployment/install docs, release notes, ADR links, and diagrams impacted by change.
- **Tracking & Publication:** Docs stored in repo with version control; published to documentation portal aligned with release tag; changelog entries linked to relevant sections for discoverability.
