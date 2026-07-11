#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: install-os-packages.sh [--dry-run] [--help]

Install the reviewed Debian/Ubuntu packages required by native CAPO. Repeated
runs skip installed packages and preserve the existing service account/paths.
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

run() {
  if "$DRY_RUN"; then
    printf 'DRY-RUN:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'CAPO package installation requires Linux'
[[ -r /etc/os-release ]] || die 'cannot identify the Linux distribution'
# shellcheck disable=SC1091
source /etc/os-release
case "${ID:-}" in
  debian|ubuntu) ;;
  *) die "unsupported distribution: ${ID:-unknown}; expected Debian or Ubuntu" ;;
esac
command -v dpkg-query >/dev/null || die 'dpkg-query is required'
command -v apt-get >/dev/null || die 'apt-get is required'

if ((EUID == 0)); then
  PRIV=()
else
  command -v sudo >/dev/null || die 'run as root or install sudo'
  PRIV=(sudo)
fi

packages=(
  ca-certificates curl git jq
  build-essential pkg-config libssl-dev libpq-dev
  python3 python3-dev python3-pip python3-venv
  nodejs npm
  cargo rustc
  postgresql postgresql-client redis-server redis-tools
)
missing=()
for package in "${packages[@]}"; do
  if dpkg-query -W -f='${db:Status-Abbrev}' "$package" 2>/dev/null | grep -q '^ii '; then
    printf 'present: %s\n' "$package"
  else
    missing+=("$package")
  fi
done

if ((${#missing[@]})); then
  run "${PRIV[@]}" apt-get update
  run "${PRIV[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"
else
  printf 'All reviewed OS packages are already installed.\n'
fi

if ! "$DRY_RUN"; then
  for executable in git curl jq python3 node npm cargo rustc psql redis-cli; do
    command -v "$executable" >/dev/null || die "installed package did not provide: $executable"
  done
fi

if id omertaos >/dev/null 2>&1; then
  [[ "$(id -u omertaos)" -ne 0 ]] || die 'omertaos must not be root'
  printf 'present: service account omertaos\n'
else
  run "${PRIV[@]}" useradd --system --user-group --home-dir /var/lib/omertaos --create-home --shell /usr/sbin/nologin omertaos
fi

run "${PRIV[@]}" install -d -o omertaos -g omertaos -m 0750 /var/lib/omertaos
run "${PRIV[@]}" install -d -o root -g omertaos -m 0750 /etc/omertaos

printf 'CAPO OS package and account checks completed.\n'
