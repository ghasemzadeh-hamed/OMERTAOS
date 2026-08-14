#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
CHECK_ONLY=false
PROFILE=lite
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_FILE="$(cd -- "$SCRIPT_DIR/../packages" && pwd)/apt-build-packages.txt"

usage() {
  cat <<'EOF'
Usage: install-os-packages.sh [--profile lite|full|enterprise] [--dry-run|--check] [--help]

Install the reviewed N2 build prerequisites on Debian/Ubuntu. Repeated runs
skip installed packages. --check is read-only; --dry-run previews mutations.
This stage never installs data servers, starts services, or adds third-party
package repositories.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
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
    --profile)
      (($# >= 2)) || die '--profile requires a value'
      PROFILE="$2"
      shift
      ;;
    --dry-run) DRY_RUN=true ;;
    --check) CHECK_ONLY=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done
"$DRY_RUN" && "$CHECK_ONLY" && die '--dry-run and --check are mutually exclusive'
[[ -r "$PACKAGE_FILE" ]] || die "package manifest is missing: $PACKAGE_FILE"
bash "$SCRIPT_DIR/preflight.sh" --profile "$PROFILE"

if ((EUID == 0)); then
  PRIV=()
else
  command -v sudo >/dev/null || die 'run as root or install sudo'
  PRIV=(sudo)
fi

packages=()
while IFS= read -r package || [[ -n "$package" ]]; do
  package="${package%%#*}"
  package="${package//[[:space:]]/}"
  [[ -n "$package" ]] && packages+=("$package")
done < "$PACKAGE_FILE"
((${#packages[@]})) || die 'package manifest is empty'

verify_python_version() {
  local version
  version="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  python3 -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info < (3, 13) else 1)' \
    || die "Python $version violates N1 requirement >=3.11,<3.13"
}

verify_node_version() {
  local major
  major="$(node -p 'Number(process.versions.node.split(".")[0])')"
  [[ "$major" == 22 ]] || die "Node.js $(node --version) violates N1 Node 22 requirement"
}

# Reject an incompatible preinstalled toolchain before package mutation.
command -v python3 >/dev/null && verify_python_version
command -v node >/dev/null && verify_node_version

for forbidden in postgresql redis-server docker.io podman; do
  for package in "${packages[@]}"; do
    [[ "$package" != "$forbidden" ]] || die "N2 manifest contains N3/service package: $package"
  done
done

missing=()
for package in "${packages[@]}"; do
  if dpkg-query -W -f='${db:Status-Abbrev}' "$package" 2>/dev/null | grep -q '^ii '; then
    printf 'present: %s\n' "$package"
  else
    missing+=("$package")
  fi
done

if "$CHECK_ONLY"; then
  ((${#missing[@]} == 0)) || die "missing N2 packages: ${missing[*]}"
elif ((${#missing[@]})); then
  run "${PRIV[@]}" apt-get update
  if ! "$DRY_RUN"; then
    for package in "${missing[@]}"; do
      case "$package" in
        python3)
          candidate="$(apt-cache policy python3 | awk '/Candidate:/ {print $2; exit}')"
          [[ -n "$candidate" && "$candidate" != '(none)' ]] || die 'APT has no Python candidate'
          dpkg --compare-versions "$candidate" ge '3.11~' && dpkg --compare-versions "$candidate" lt '3.13~' \
            || die "APT Python candidate $candidate violates N1 requirement >=3.11,<3.13"
          ;;
        nodejs)
          candidate="$(apt-cache policy nodejs | awk '/Candidate:/ {print $2; exit}')"
          [[ -n "$candidate" && "$candidate" != '(none)' ]] || die 'APT has no Node.js candidate'
          dpkg --compare-versions "$candidate" ge '22~' && dpkg --compare-versions "$candidate" lt '23~' \
            || die "APT Node.js candidate $candidate violates N1 Node 22 requirement"
          ;;
      esac
    done
  fi
  run "${PRIV[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"
else
  printf 'All reviewed N2 packages are already installed.\n'
fi

verify_toolchains() {
  local python_version
  for executable in git curl jq python3 node npm corepack cargo rustc psql redis-cli rsync flock; do
    command -v "$executable" >/dev/null || die "N1 toolchain command is unavailable: $executable"
  done
  python_version="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  verify_python_version
  verify_node_version
  printf 'toolchains: Python %s; Node %s; npm %s; rustc %s; cargo %s\n' \
    "$python_version" "$(node --version)" "$(npm --version)" "$(rustc --version)" "$(cargo --version)"
}

if "$DRY_RUN"; then
  printf 'DRY-RUN: post-install N1 toolchain version verification\n'
else
  verify_toolchains
fi

if id omertaos >/dev/null 2>&1; then
  [[ "$(id -u omertaos)" -ne 0 ]] || die 'omertaos must not be root'
  printf 'present: service account omertaos\n'
else
  "$CHECK_ONLY" && die 'service account omertaos is missing'
  run "${PRIV[@]}" useradd --system --user-group --home-dir /var/lib/omertaos --create-home --shell /usr/sbin/nologin omertaos
fi

if "$CHECK_ONLY"; then
  for path in /etc/omertaos /var/lib/omertaos /var/log/omertaos /var/lib/omertaos/backups; do
    [[ -d "$path" ]] || die "required Native path is missing: $path"
  done
else
  run "${PRIV[@]}" install -d -o omertaos -g omertaos -m 0750 /var/lib/omertaos
  run "${PRIV[@]}" install -d -o omertaos -g omertaos -m 0750 /var/log/omertaos
  run "${PRIV[@]}" install -d -o omertaos -g omertaos -m 0750 /var/lib/omertaos/backups
  run "${PRIV[@]}" install -d -o root -g omertaos -m 0750 /etc/omertaos
fi

printf 'N2 package, toolchain, account, and path checks completed; no services were started.\n'
