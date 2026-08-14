#!/usr/bin/env bash
set -euo pipefail

PROFILE=lite
MIN_FREE_KIB=$((5 * 1024 * 1024))

usage() {
  cat <<'EOF'
Usage: preflight.sh [--profile lite|full|enterprise] [--help]

Read-only N2 preflight for a Native Debian/Ubuntu host. It validates platform,
architecture, systemd, cgroups v2, APT tooling, and free disk space. It does not
install packages or start services.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

while (($#)); do
  case "$1" in
    --profile)
      (($# >= 2)) || die '--profile requires a value'
      PROFILE="$2"
      shift
      ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

case "$PROFILE" in lite|full|enterprise) ;; *) die "unsupported profile: $PROFILE" ;; esac
[[ "$(uname -s)" == Linux ]] || die 'Native installation requires Linux'
[[ -r /etc/os-release ]] || die 'cannot identify the Linux distribution'
# shellcheck disable=SC1091
source /etc/os-release
case "${ID:-}:${VERSION_ID:-}" in
  debian:12|ubuntu:22.04|ubuntu:24.04) ;;
  *) die "unsupported platform: ${ID:-unknown} ${VERSION_ID:-unknown}" ;;
esac

case "$(uname -m)" in x86_64|aarch64) ;; *) die "unsupported architecture: $(uname -m)" ;; esac
[[ -d /run/systemd/system ]] || die 'systemd must be PID 1 on the Native target'
[[ -r /sys/fs/cgroup/cgroup.controllers ]] || die 'cgroups v2 is required by Runtime isolation'
for executable in apt-get apt-cache dpkg dpkg-query df getent install ps useradd; do
  command -v "$executable" >/dev/null || die "required host command is missing: $executable"
done
[[ "$(ps -p 1 -o comm= | tr -d '[:space:]')" == systemd ]] || die 'systemd must be PID 1 on the Native target'

probe=/opt
[[ -d "$probe" ]] || probe=/
free_kib="$(df -Pk "$probe" | awk 'NR == 2 {print $4}')"
[[ "$free_kib" =~ ^[0-9]+$ ]] || die "cannot determine free space for $probe"
((free_kib >= MIN_FREE_KIB)) || die 'at least 5 GiB free space is required for Native build/install'

printf 'Native preflight passed: %s %s, %s, profile=%s, free=%s KiB\n' \
  "$ID" "$VERSION_ID" "$(uname -m)" "$PROFILE" "$free_kib"
