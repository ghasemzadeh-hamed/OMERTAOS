#!/usr/bin/env bash
set -euo pipefail

MODE=native
EXPECTED_COMMIT=

usage() {
  cat <<'EOF'
Usage: validate-environment.sh [--mode native|simulation] [--expected-commit SHA] [--help]

Read-only N1 host validation. It checks the supported OS, systemd, cgroups v2,
users, canonical path/port boundaries, secret-directory ownership, exact release
commit, and installed tool versions. Tools and paths owned by N2/N4 are reported
as deferred when they are not installed yet; this script never installs them.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
defer() { DEFERRED+=("$1"); printf 'deferred=%s\n' "$1"; }

while (($#)); do
  case "$1" in
    --mode)
      (($# >= 2)) || die '--mode requires a value'
      MODE="$2"
      shift
      ;;
    --expected-commit)
      (($# >= 2)) || die '--expected-commit requires a value'
      EXPECTED_COMMIT="$2"
      shift
      ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

case "$MODE" in native|simulation) ;; *) die "unsupported mode: $MODE" ;; esac
[[ -z "$EXPECTED_COMMIT" || "$EXPECTED_COMMIT" =~ ^[0-9a-f]{40}$ ]] || die 'expected commit must be a full Git SHA'
DEFERRED=()

for command in getent git ps ss stat uname; do
  command -v "$command" >/dev/null || die "required N1 command is missing: $command"
done

[[ -r /etc/os-release ]] || die 'cannot identify the Linux distribution'
# shellcheck disable=SC1091
source /etc/os-release
case "${ID:-}:${VERSION_ID:-}" in
  debian:12|ubuntu:22.04|ubuntu:24.04) ;;
  *) die "unsupported platform: ${ID:-unknown} ${VERSION_ID:-unknown}" ;;
esac
case "$(uname -m)" in x86_64|aarch64) ;; *) die "unsupported architecture: $(uname -m)" ;; esac
[[ "$(ps -p 1 -o comm= | tr -d '[:space:]')" == systemd ]] || die 'systemd must be PID 1'
[[ "$(stat -fc %T /sys/fs/cgroup)" == cgroup2fs ]] || die 'cgroups v2 is required'

getent passwd omerta >/dev/null || die 'acceptance operator omerta is missing'
if getent passwd omertaos >/dev/null; then
  [[ "$(id -u omertaos)" != 0 ]] || die 'omertaos service account must not be root'
  printf 'service_user=present-non-root\n'
else
  defer 'service-user-to-N2'
fi

[[ -d /etc/omertaos ]] || die '/etc/omertaos is missing'
[[ "$(stat -c '%a:%U:%G' /etc/omertaos)" == '750:root:root' ]] || die '/etc/omertaos must be 0750 root:root before secrets are rendered'
if find /etc/omertaos -mindepth 1 -maxdepth 1 -type f -print -quit | grep -q .; then
  die 'N1 expects no rendered secret files before the strict environment phase'
fi

for path_phase in '/opt/omertaos:N8' '/var/lib/omertaos:N2' '/var/log/omertaos:N2'; do
  path="${path_phase%%:*}"
  phase="${path_phase##*:}"
  if [[ -e "$path" ]]; then
    [[ ! -L "$path" ]] || die "pre-install path must not be a symlink yet: $path"
    printf 'path_present=%s\n' "$path"
  else
    defer "${path}-to-${phase}"
  fi
done

RELEASE_ROOT=/srv/omertaos-source
[[ -d "$RELEASE_ROOT/.git" ]] || die 'clean acceptance release clone is missing'
ACTUAL_COMMIT="$(git -c safe.directory="$RELEASE_ROOT" -C "$RELEASE_ROOT" rev-parse HEAD)"
[[ -z "$(git -c safe.directory="$RELEASE_ROOT" -C "$RELEASE_ROOT" status --porcelain)" ]] || die 'acceptance release clone is dirty'
[[ -z "$EXPECTED_COMMIT" || "$ACTUAL_COMMIT" == "$EXPECTED_COMMIT" ]] || die "release commit mismatch: $ACTUAL_COMMIT"

for port in 3000 5432 6379 8000 8080 50051; do
  if ss -H -ltn | awk '{print $4}' | grep -Eq "(^|:)$port$"; then
    die "canonical pre-install port is already occupied: $port"
  fi
done

if command -v python3 >/dev/null; then
  python_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  case "$python_version" in 3.11|3.12) ;; *) die "unsupported Python version: $python_version" ;; esac
  printf 'python=%s\n' "$python_version"
else
  defer 'python-3.11-or-3.12-to-N2'
fi

if command -v node >/dev/null; then
  node_major="$(node --version | sed -E 's/^v([0-9]+).*/\1/')"
  [[ "$node_major" == 22 ]] || die "Node 22 LTS is required, got $(node --version)"
  printf 'node=%s\n' "$(node --version)"
else
  defer 'node-22-to-N2'
fi

if command -v cargo >/dev/null || command -v rustc >/dev/null; then
  command -v cargo >/dev/null && command -v rustc >/dev/null || die 'cargo and rustc must be installed together'
  printf 'cargo=%s\n' "$(cargo --version)"
  printf 'rustc=%s\n' "$(rustc --version)"
else
  defer 'rust-stable-to-N2/N4'
fi

printf 'os=%s %s\n' "$ID" "$VERSION_ID"
printf 'architecture=%s\n' "$(uname -m)"
printf 'pid1=systemd\n'
printf 'cgroup=cgroup2fs\n'
printf 'ports=3000,5432,6379,8000,8080,50051-free\n'
printf 'secret_dir=750:root:root-empty\n'
printf 'repo_sha=%s\n' "$ACTUAL_COMMIT"
printf 'N1 environment contract passed: mode=%s deferred=%s\n' "$MODE" "${#DEFERRED[@]}"
