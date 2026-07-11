#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
ROOT="${OMERTAOS_ROOT:-/opt/omertaos/OMERTAOS}"

usage() {
  cat <<'EOF'
Usage: install-node-services.sh [--root PATH] [--dry-run] [--help]

Install and build the canonical gateway/ and console/ services. Console uses
its committed pnpm lockfile. Gateway has no committed npm lockfile, so npm
install is used and the absence is reported rather than pretending npm ci is safe.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
run() {
  if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "$@"; printf '\n'; else "$@"; fi
}

while (($#)); do
  case "$1" in
    --root) (($# >= 2)) || die '--root requires a path'; ROOT="$2"; shift ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'CAPO application installation requires Linux'
command -v node >/dev/null || die 'node is required; run install-os-packages.sh first'
command -v npm >/dev/null || die 'npm is required; run install-os-packages.sh first'
[[ -f "$ROOT/gateway/package.json" ]] || die 'gateway/package.json is missing'
[[ -f "$ROOT/console/package.json" ]] || die 'console/package.json is missing'
[[ -f "$ROOT/console/pnpm-lock.yaml" ]] || die 'console/pnpm-lock.yaml is required'

node_major="$(node -p 'Number(process.versions.node.split(".")[0])')"
((node_major >= 18)) || die 'Node.js 18 or newer is required'

if [[ -f "$ROOT/gateway/package-lock.json" || -f "$ROOT/gateway/npm-shrinkwrap.json" ]]; then
  run npm ci --prefix "$ROOT/gateway"
else
  printf 'Gateway has no committed npm lockfile; using npm install.\n'
  run npm install --prefix "$ROOT/gateway" --no-audit --no-fund
fi
run npm run build --prefix "$ROOT/gateway"

command -v corepack >/dev/null || die 'corepack is required for the committed Console pnpm lockfile'
run corepack pnpm --dir "$ROOT/console" install --frozen-lockfile
run corepack pnpm --dir "$ROOT/console" run prisma:generate
run corepack pnpm --dir "$ROOT/console" run build

if ! "$DRY_RUN"; then
  [[ -f "$ROOT/gateway/dist/server.js" ]] || die 'Gateway build did not create dist/server.js'
  [[ -d "$ROOT/console/.next" ]] || die 'Console build did not create .next'
fi

printf 'CAPO Gateway and Console installation checks completed.\n'
