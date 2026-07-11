#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
ENV_FILE=/etc/omertaos/omertaos.env

usage() {
  cat <<'EOF'
Usage: install-data-services.sh [--env-file PATH] [--dry-run] [--help]

Start and validate native PostgreSQL/Redis, then create the configured CAPO
PostgreSQL login role and database only when absent. Existing passwords and
database contents are preserved. Run install-os-packages.sh first.
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
    --env-file)
      (($# >= 2)) || die '--env-file requires a path'
      ENV_FILE=$2
      shift
      ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'CAPO data installation requires Linux'
[[ -r /etc/os-release ]] || die 'cannot identify the Linux distribution'
# shellcheck disable=SC1091
source /etc/os-release
case "${ID:-}" in
  debian|ubuntu) ;;
  *) die "unsupported distribution: ${ID:-unknown}; expected Debian or Ubuntu" ;;
esac
[[ -r "$ENV_FILE" ]] || die "environment file is not readable: $ENV_FILE"

set -a
# The operator-owned root-readable file is trusted configuration.
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

CAPO_POSTGRES_ROLE=${CAPO_POSTGRES_ROLE:-omertaos}
CAPO_POSTGRES_DATABASE=${CAPO_POSTGRES_DATABASE:-omertaos}
CAPO_POSTGRES_PASSWORD=${CAPO_POSTGRES_PASSWORD:-}
[[ "$CAPO_POSTGRES_ROLE" =~ ^[a-z_][a-z0-9_]*$ ]] || die 'CAPO_POSTGRES_ROLE is not a safe PostgreSQL identifier'
[[ "$CAPO_POSTGRES_DATABASE" =~ ^[a-z_][a-z0-9_]*$ ]] || die 'CAPO_POSTGRES_DATABASE is not a safe PostgreSQL identifier'
[[ -n "$CAPO_POSTGRES_PASSWORD" && "$CAPO_POSTGRES_PASSWORD" != CHANGE_ME ]] || die 'set CAPO_POSTGRES_PASSWORD to a real secret outside Git'

for executable in systemctl psql pg_isready redis-cli; do
  command -v "$executable" >/dev/null || die "missing required executable: $executable"
done
id postgres >/dev/null 2>&1 || die 'PostgreSQL system account is missing'

if ((EUID == 0)); then
  PRIV=()
  command -v runuser >/dev/null || die 'runuser is required when running as root'
  AS_POSTGRES=(runuser --preserve-environment -u postgres --)
else
  command -v sudo >/dev/null || die 'run as root or install sudo'
  PRIV=(sudo)
  AS_POSTGRES=(sudo --preserve-env=CAPO_POSTGRES_ROLE,CAPO_POSTGRES_DATABASE,CAPO_POSTGRES_PASSWORD -u postgres)
fi

run "${PRIV[@]}" systemctl enable --now postgresql.service
run "${PRIV[@]}" systemctl enable --now redis-server.service

if "$DRY_RUN"; then
  printf 'DRY-RUN: validate PostgreSQL readiness, create missing role/database, verify ownership, and require Redis PONG\n'
  printf 'Optional MongoDB, Qdrant, and MinIO remain disabled unless explicitly configured.\n'
  exit 0
fi

pg_isready -q || die 'PostgreSQL is not ready'
[[ "$(redis-cli --raw ping)" == PONG ]] || die 'Redis did not return PONG'

export CAPO_POSTGRES_ROLE CAPO_POSTGRES_DATABASE CAPO_POSTGRES_PASSWORD
"${AS_POSTGRES[@]}" psql --no-psqlrc --set=ON_ERROR_STOP=1 <<'SQL'
\getenv role_name CAPO_POSTGRES_ROLE
\getenv role_password CAPO_POSTGRES_PASSWORD
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'role_name', :'role_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'role_name') \gexec
SELECT rolcanlogin AS can_login
FROM pg_roles WHERE rolname = :'role_name' \gset role_
\if :role_can_login
\else
  \warn 'Configured PostgreSQL role exists but cannot log in.'
  \quit 2
\endif
SQL

# CREATE DATABASE cannot run inside a transaction; psql's \gexec executes it as
# a standalone statement and only when the database is absent.
"${AS_POSTGRES[@]}" psql --no-psqlrc --set=ON_ERROR_STOP=1 <<'SQL'
\getenv db_name CAPO_POSTGRES_DATABASE
\getenv role_name CAPO_POSTGRES_ROLE
SELECT format('CREATE DATABASE %I OWNER %I', :'db_name', :'role_name')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'db_name') \gexec
SELECT CASE WHEN pg_get_userbyid(datdba) = :'role_name' THEN 1 ELSE 0 END AS owner_matches
FROM pg_database WHERE datname = :'db_name' \gset db_
\if :db_owner_matches
\else
  \warn 'Configured database exists but is owned by another role.'
  \quit 3
\endif
SQL

"${AS_POSTGRES[@]}" psql --no-psqlrc --set=ON_ERROR_STOP=1 \
  --dbname="$CAPO_POSTGRES_DATABASE" --command='SELECT 1' >/dev/null

printf 'PostgreSQL role/database and Redis readiness checks completed.\n'
printf 'MongoDB, Qdrant, and MinIO are optional; disabled services remain explicit degraded capabilities.\n'
