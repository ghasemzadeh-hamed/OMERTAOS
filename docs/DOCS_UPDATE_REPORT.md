# Docs update report

## Files changed
- README.md
- docs/quickstart.md
- docs/install/docker.md
- docs/install/native.md
- docs/install/wsl.md
- Removed legacy `docs/audit/` directory

## Corrections applied
- Updated quickstart guidance to match `quick-install` behavior, the `docker-compose.quickstart.yml` services, and current ports (control 8000, gateway 8080, console 3000).
- Replaced outdated Compose and `.env` references with the current `dev.env` workflow and the quick-install scripts on Linux, Windows, and WSL.
- Aligned Docker and native installation steps with present prerequisites and health checks.
- Removed non-English content and legacy audit references to comply with ASCII-only documentation requirements.

## Removed or deprecated items
- Deleted the `docs/audit/` folder because audit bundles are no longer supported by the current documentation policy.
- Marked Windows native services without Docker as UNVERIFIED pending validation.
- Noted ISO/kiosk instructions as UNVERIFIED because release artifacts are not present in the repository.

## Remaining UNVERIFIED items
- ISO/kiosk installation details (pending release artifact verification).
- Legacy Windows service installation flow (`scripts/install_win.ps1`).
