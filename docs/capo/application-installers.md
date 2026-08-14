# Native application installers

N4 provides one installer per canonical service boundary:

```text
install-console.sh -> install-gateway.sh -> install-control.sh -> install-runtime.sh
```

All four support `--dry-run` and read-only `--check`, build as the non-root
`omertaos` account, verify their expected artifacts, and never start services.
Control creates its Python virtualenv; Gateway uses `npm ci`; Console uses the
committed pnpm lock and generates Prisma client code without running migrations;
Runtime requires a Cargo lock and installs only the release binary.

The legacy installer names and CAPO paths are compatibility wrappers around
`deploy/native/scripts/`. N5 separately owns database migrations/bootstrap and
N6 owns systemd wiring. A failed N4 build must leave `/etc/omertaos`, databases,
and `/var/lib/omertaos` persistent data intact; rebuild from the prior reviewed
revision rather than deleting state.

Windows build evidence does not prove Linux ownership, dynamic linking, or
installed binary execution. Those checks remain mandatory on the intended
Debian/Ubuntu host.

Current D6 workstation result: locked metadata and formatting pass, but both
`cargo test --locked --all-targets` and `cargo build --locked --release` stop
before linking because the Windows MSVC `link.exe`/Visual C++ Build Tools are
not installed. The system drive is also full, so Cargo cannot update cache
last-use metadata. This is an environment blocker, not N4 acceptance; rerun on
the intended Linux host or after provisioning the reviewed Windows linker/SDK
and sufficient disk space.
