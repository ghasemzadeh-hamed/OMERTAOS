#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
CHECK_ONLY=false
PROFILE=lite
INSTALLER_ENV=/etc/omertaos/installer.env
CONTROL_ENV=/etc/omertaos/control.env
CONSOLE_ENV=/etc/omertaos/console.env
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_VALIDATOR="$SCRIPT_DIR/../env/validate_data_env.py"

usage() {
  cat <<'EOF'
Usage: install-data-services.sh [--profile lite|full|enterprise]
       [--installer-env PATH] [--control-env PATH] [--console-env PATH]
       [--dry-run|--check] [--help]

Install and activate native PostgreSQL/Redis, then create the distinct Control
and Console login roles/databases only when absent. Existing credentials,
owners, schemas, and data are never changed. --check is completely read-only.
N5 owns schema migrations and application bootstrap.
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
    --profile) (($# >= 2)) || die '--profile requires a value'; PROFILE="$2"; shift ;;
    --installer-env|--env-file) (($# >= 2)) || die "$1 requires a path"; INSTALLER_ENV="$2"; shift ;;
    --control-env) (($# >= 2)) || die '--control-env requires a path'; CONTROL_ENV="$2"; shift ;;
    --console-env) (($# >= 2)) || die '--console-env requires a path'; CONSOLE_ENV="$2"; shift ;;
    --dry-run) DRY_RUN=true ;;
    --check) CHECK_ONLY=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done
"$DRY_RUN" && "$CHECK_ONLY" && die '--dry-run and --check are mutually exclusive'
case "$PROFILE" in lite|full|enterprise) ;; *) die "unsupported profile: $PROFILE" ;; esac
bash "$SCRIPT_DIR/preflight.sh" --profile "$PROFILE"
((EUID == 0)) || die 'run as root so installer credentials remain root-readable only'
for path in "$INSTALLER_ENV" "$CONTROL_ENV" "$CONSOLE_ENV"; do
  [[ -r "$path" ]] || die "environment file is not readable: $path"
done
python3 "$ENV_VALIDATOR" --installer "$INSTALLER_ENV" --control "$CONTROL_ENV" --console "$CONSOLE_ENV"

declare -A CONFIG=()
while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%$'\r'}"
  [[ -z "$line" || "$line" == \#* ]] && continue
  [[ "$line" =~ ^[A-Z][A-Z0-9_]*=.*$ ]] || die "$INSTALLER_ENV contains an invalid assignment"
  key="${line%%=*}"
  value="${line#*=}"
  [[ ! -v "CONFIG[$key]" ]] || die "$INSTALLER_ENV contains duplicate key: $key"
  CONFIG["$key"]="$value"
done < "$INSTALLER_ENV"

required=(
  OMERTAOS_POSTGRES_ROLE OMERTAOS_POSTGRES_DATABASE OMERTAOS_POSTGRES_PASSWORD
  OMERTAOS_CONSOLE_POSTGRES_ROLE OMERTAOS_CONSOLE_POSTGRES_DATABASE OMERTAOS_CONSOLE_POSTGRES_PASSWORD
)
for key in "${required[@]}"; do [[ -n "${CONFIG[$key]:-}" ]] || die "$INSTALLER_ENV is missing $key"; done

packages=(postgresql postgresql-client redis-server redis-tools iproute2)
missing=()
for package in "${packages[@]}"; do
  if dpkg-query -W -f='${db:Status-Abbrev}' "$package" 2>/dev/null | grep -q '^ii '; then
    printf 'present: %s\n' "$package"
  else
    missing+=("$package")
  fi
done

POLICY_PATH=/usr/sbin/policy-rc.d
POLICY_MARKER='# OMERTAOS N3 temporary no-start policy'
POLICY_CREATED=false
cleanup_policy() {
  if "$POLICY_CREATED"; then
    if [[ -f "$POLICY_PATH" ]] && grep -Fqx "$POLICY_MARKER" "$POLICY_PATH"; then
      unlink "$POLICY_PATH"
    else
      printf 'WARNING: temporary service policy changed externally; preserving it for review\n' >&2
    fi
    POLICY_CREATED=false
  fi
}
trap cleanup_policy EXIT

if "$CHECK_ONLY"; then
  ((${#missing[@]} == 0)) || die "missing N3 packages: ${missing[*]}"
elif ((${#missing[@]})); then
  run apt-get update
  if "$DRY_RUN"; then
    printf 'DRY-RUN: install a temporary policy-rc.d guard so packages cannot auto-start services\n'
    run env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"
  else
    if [[ -e "$POLICY_PATH" || -L "$POLICY_PATH" ]]; then
      [[ -x "$POLICY_PATH" ]] || die 'existing policy-rc.d is not executable'
      if "$POLICY_PATH" postgresql start; then
        policy_status=0
      else
        policy_status=$?
      fi
      [[ "$policy_status" == 101 ]] || die 'existing policy-rc.d does not block package service starts'
    else
      policy_tmp="$(mktemp)"
      printf '#!/bin/sh\n%s\nexit 101\n' "$POLICY_MARKER" > "$policy_tmp"
      install -o root -g root -m 0755 "$policy_tmp" "$POLICY_PATH"
      unlink "$policy_tmp"
      POLICY_CREATED=true
    fi
    env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"
    cleanup_policy
  fi
else
  printf 'All reviewed N3 data packages are already installed.\n'
fi

if "$DRY_RUN"; then
  run systemctl enable --now postgresql.service
  run systemctl enable --now redis-server.service
  printf 'DRY-RUN: verify loopback listeners/readiness/persistence and provision two missing role/database pairs\n'
  printf 'DRY-RUN: no schemas, migrations, seed data, or password rotation\n'
  exit 0
fi

for executable in systemctl psql pg_isready pg_lsclusters pg_conftool redis-cli ss runuser awk sed tail; do
  command -v "$executable" >/dev/null || die "missing required executable after N3 package install: $executable"
done
id postgres >/dev/null 2>&1 || die 'PostgreSQL system account is missing'

validate_postgres_bind() {
  local found=false version cluster value address
  while read -r version cluster _; do
    [[ -n "$version" && -n "$cluster" ]] || continue
    found=true
    value="$(pg_conftool "$version" "$cluster" show listen_addresses | awk -F= '{print $2}' | tr -d " '\"")"
    [[ -n "$value" ]] || value=localhost
    IFS=',' read -r -a addresses <<< "$value"
    for address in "${addresses[@]}"; do
      case "$address" in localhost|127.0.0.1|::1) ;; *) die "PostgreSQL cluster $version/$cluster has unsafe listen_addresses" ;; esac
    done
  done < <(pg_lsclusters --no-header)
  "$found" || die 'no PostgreSQL cluster was created'
}

validate_redis_bind() {
  local config=/etc/redis/redis.conf bind_line protected address
  [[ -r "$config" ]] || die 'Redis configuration is missing'
  bind_line="$(awk '$1 == "bind" {line=$0} END {print line}' "$config")"
  protected="$(awk '$1 == "protected-mode" {value=$2} END {print value}' "$config")"
  [[ -n "$bind_line" ]] || die 'Redis bind is not explicit; refusing a possible all-interface listener'
  read -r -a addresses <<< "${bind_line#bind }"
  for address in "${addresses[@]}"; do
    case "$address" in 127.0.0.1|::1|-::1|localhost) ;; *) die 'Redis configuration contains a non-loopback bind' ;; esac
  done
  [[ "$protected" == yes ]] || die 'Redis protected-mode must be yes'
}

validate_postgres_bind
validate_redis_bind

if "$CHECK_ONLY"; then
  systemctl is-enabled --quiet postgresql.service || die 'PostgreSQL is not enabled'
  systemctl is-enabled --quiet redis-server.service || die 'Redis is not enabled'
  systemctl is-active --quiet postgresql.service || die 'PostgreSQL is not active'
  systemctl is-active --quiet redis-server.service || die 'Redis is not active'
else
  systemctl enable --now postgresql.service
  systemctl enable --now redis-server.service
fi

pg_isready --host=127.0.0.1 --port=5432 --quiet || die 'PostgreSQL is not ready on loopback'
[[ "$(redis-cli --host 127.0.0.1 --port 6379 --raw ping)" == PONG ]] || die 'Redis did not return PONG on loopback'

check_loopback_listener() {
  local port="$1" service="$2" addresses address
  addresses="$(ss -H -ltn | awk -v suffix=":$port" 'substr($4, length($4)-length(suffix)+1) == suffix {print $4}')"
  [[ -n "$addresses" ]] || die "$service has no TCP listener on port $port"
  while IFS= read -r address; do
    case "$address" in 127.0.0.1:"$port"|\[::1\]:"$port") ;; *) die "$service exposes a non-loopback listener: $address" ;; esac
  done <<< "$addresses"
}
check_loopback_listener 5432 PostgreSQL
check_loopback_listener 6379 Redis

redis_save="$(redis-cli --host 127.0.0.1 --port 6379 --raw CONFIG GET save | tail -n 1)"
[[ -n "$redis_save" ]] || die 'Redis snapshot persistence is disabled; configure an RDB save policy'

AS_POSTGRES=(runuser -u postgres --)
provision_database() {
  local role="$1" database="$2" password="$3" password_literal
  password_literal="$(printf '%s' "$password" | sed "s/'/''/g")"
  "${AS_POSTGRES[@]}" psql --no-psqlrc --set=ON_ERROR_STOP=1 <<SQL
SET standard_conforming_strings = on;
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', '$role', '$password_literal')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$role') \gexec
SELECT COALESCE((SELECT rolcanlogin::int FROM pg_roles WHERE rolname = '$role'), 0) AS valid \gset role_
\if :role_valid
\else
  \warn 'Configured PostgreSQL role is missing or cannot log in.'
  \quit 2
\endif
SQL
  "${AS_POSTGRES[@]}" psql --no-psqlrc --set=ON_ERROR_STOP=1 <<SQL
SELECT format('CREATE DATABASE %I OWNER %I', '$database', '$role')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$database') \gexec
SELECT COALESCE((SELECT (pg_get_userbyid(datdba) = '$role')::int
  FROM pg_database WHERE datname = '$database'), 0) AS valid \gset db_
\if :db_valid
\else
  \warn 'Configured database is missing or owned by another role.'
  \quit 3
\endif
SQL
  PGPASSWORD="$password" psql --no-psqlrc --set=ON_ERROR_STOP=1 \
    --host=127.0.0.1 --port=5432 --username="$role" --dbname="$database" \
    --command='SELECT 1' >/dev/null
}

check_database() {
  local role="$1" database="$2" password="$3"
  "${AS_POSTGRES[@]}" psql --no-psqlrc --set=ON_ERROR_STOP=1 <<SQL
SELECT COALESCE((SELECT rolcanlogin::int FROM pg_roles WHERE rolname = '$role'), 0) AS valid \gset role_
\if :role_valid
\else
  \quit 2
\endif
SELECT COALESCE((SELECT (pg_get_userbyid(datdba) = '$role')::int
  FROM pg_database WHERE datname = '$database'), 0) AS valid \gset db_
\if :db_valid
\else
  \quit 3
\endif
SQL
  PGPASSWORD="$password" psql --no-psqlrc --set=ON_ERROR_STOP=1 \
    --host=127.0.0.1 --port=5432 --username="$role" --dbname="$database" \
    --command='SELECT 1' >/dev/null
}

action=provision_database
"$CHECK_ONLY" && action=check_database
"$action" "${CONFIG[OMERTAOS_POSTGRES_ROLE]}" "${CONFIG[OMERTAOS_POSTGRES_DATABASE]}" "${CONFIG[OMERTAOS_POSTGRES_PASSWORD]}"
"$action" "${CONFIG[OMERTAOS_CONSOLE_POSTGRES_ROLE]}" "${CONFIG[OMERTAOS_CONSOLE_POSTGRES_DATABASE]}" "${CONFIG[OMERTAOS_CONSOLE_POSTGRES_PASSWORD]}"
unset PGPASSWORD

printf 'N3 PostgreSQL/Redis checks passed; existing data and credentials were preserved.\n'
if [[ "$PROFILE" != lite ]]; then
  printf 'MongoDB, Qdrant, and MinIO remain explicitly disabled until separate endpoint, backup, and rollback acceptance.\n'
fi
trap - EXIT
