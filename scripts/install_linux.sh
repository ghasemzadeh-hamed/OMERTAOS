#!/usr/bin/env bash
# DEPRECATED: use scripts/quicksetup.sh for Docker-based deployments. This script remains for
# legacy native installs and will be removed in a future release.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"
COMMON_LIB="${LIB_DIR}/common.sh"

if [[ -f "${COMMON_LIB}" ]]; then
  # shellcheck source=lib/common.sh
  source "${COMMON_LIB}"
  log_warn "[DEPRECATED] scripts/install_linux.sh will be removed; use scripts/quicksetup.sh for container installs."
else
  echo "[WARN] scripts/install_linux.sh is deprecated; use scripts/quicksetup.sh." >&2
fi

APP_ROOT=${APP_ROOT:-/opt/omerta}
APP_USER=${APP_USER:-omerta}
APP_GROUP=${APP_GROUP:-www-data}
REPO=${REPO:-https://github.com/Hamedghz/OMERTAOS.git}
APP_DIR="$APP_ROOT/OMERTAOS"
ENV_FILE="$APP_DIR/.env"
SYSTEMD_DIR="$APP_DIR/configs/systemd"
CONTROL_PORT=${CONTROL_PORT:-8000}
GATEWAY_PORT=${GATEWAY_PORT:-3000}
CONSOLE_PORT=${CONSOLE_PORT:-3001}
NODE_REQUIRED_MAJOR=18
PYTHON_DEB_PACKAGES=()
PYTHON_PREFERRED_BIN=""
PYTHON_BIN="${PYTHON_BIN:-}"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

ensure_nodesource() {
  local current_major=0
  if command_exists node; then
    current_major=$(node -v | sed 's/v//' | cut -d. -f1)
  fi

  if (( current_major >= NODE_REQUIRED_MAJOR )); then
    return
  fi

  echo "Installing Node.js ${NODE_REQUIRED_MAJOR}.x from NodeSource..."
  curl -fsSL https://deb.nodesource.com/setup_${NODE_REQUIRED_MAJOR}.x | sudo -E bash -
  sudo apt install -y nodejs
}

prepare_python_packages() {
  if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    echo "Detected GitHub Actions runner; skipping Python apt packages"
    PYTHON_PREFERRED_BIN=${PYTHON_PREFERRED_BIN:-python3}
    return
  fi

  if apt-cache show python3.11 >/dev/null 2>&1; then
    PYTHON_DEB_PACKAGES=(python3.11 python3.11-venv python3.11-dev)
    PYTHON_PREFERRED_BIN="python3.11"
  else
    PYTHON_DEB_PACKAGES=(python3 python3-venv python3-dev)
    PYTHON_PREFERRED_BIN="python3"
  fi
}

select_python_binary() {
  local candidates=()

  if [[ -n "${PYTHON_BIN}" ]]; then
    candidates+=("${PYTHON_BIN}")
  fi

  if [[ -n "${PYTHON_PREFERRED_BIN}" ]]; then
    candidates+=("${PYTHON_PREFERRED_BIN}")
  fi

  candidates+=(python3.11 python3.10 python3)

  for candidate in "${candidates[@]}"; do
    if [[ -n "${candidate}" && "${candidate}" != "null" ]] && command_exists "${candidate}"; then
      PYTHON_BIN="${candidate}"
      echo "Using Python interpreter: ${PYTHON_BIN}"
      return
    fi
  done

  echo "Python 3 with venv support is required but was not found" >&2
  exit 1
}

install_system_packages() {
  echo "[install] installing system dependencies"
  sudo apt update -y

  prepare_python_packages

  local packages=(git curl ca-certificates build-essential redis-server postgresql postgresql-contrib)

  if ((${#PYTHON_DEB_PACKAGES[@]} > 0)); then
    packages+=("${PYTHON_DEB_PACKAGES[@]}")
  else
    echo "Skipping Python apt packages (already provided by environment)"
  fi

  sudo apt install -y "${packages[@]}"
}

run_as_app() {
  sudo -H -u "$APP_USER" bash -lc "$1"
}

create_service_user() {
  if ! id -u "$APP_USER" >/dev/null 2>&1; then
    echo "Creating service user $APP_USER"
    sudo useradd --system --create-home --home-dir "$APP_ROOT" --shell /usr/sbin/nologin "$APP_USER"
  fi

  if getent group "$APP_GROUP" >/dev/null 2>&1; then
    sudo usermod -a -G "$APP_GROUP" "$APP_USER" >/dev/null 2>&1 || true
  fi
}

clone_or_update_repo() {
  echo "[install] installing OMERTAOS application"
  sudo mkdir -p "$APP_ROOT"
  sudo chown "$APP_USER":"$APP_GROUP" "$APP_ROOT"

  if [ ! -d "$APP_DIR/.git" ]; then
    echo "Cloning repository into $APP_DIR"
    run_as_app "git clone '$REPO' '$APP_DIR'"
  else
    echo "Repository already present; fetching latest changes"
    run_as_app "cd '$APP_DIR' && git fetch --all --prune && git reset --hard origin/AIONOS"
  fi

  sudo chown -R "$APP_USER":"$APP_GROUP" "$APP_DIR"
}

provision_python() {
  if [ ! -d "$APP_DIR/.venv" ]; then
    echo "Creating Python virtual environment"
    local python_bin="${PYTHON_BIN:-python3}"
    run_as_app "${python_bin} -m venv '$APP_DIR/.venv'"
  fi

  echo "Installing Python dependencies (aionos-core[control])"
  run_as_app "cd '$APP_DIR' && source '$APP_DIR/.venv/bin/activate' && pip install --upgrade pip wheel setuptools && pip install '.[control]'"

  echo "Installing control package in editable mode"
  run_as_app "cd '$APP_DIR' && source '$APP_DIR/.venv/bin/activate' && pip install -e os/control"
}

ensure_pnpm() {
  if ! command_exists pnpm; then
    echo "Installing pnpm globally"
    sudo npm install -g pnpm@9 >/dev/null 2>&1 || sudo npm install -g pnpm
  fi
}

provision_node_projects() {
  ensure_pnpm

  for project in console gateway; do
    echo "Installing Node dependencies for $project"
    run_as_app "cd '$APP_DIR/$project' && if [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile; else pnpm install --no-frozen-lockfile; fi"
  done

  echo "Generating Prisma client for console"
  run_as_app "cd '$APP_DIR/console' && pnpm prisma:generate"

  echo "Building console"
  run_as_app "cd '$APP_DIR/console' && pnpm build"

  echo "Building gateway"
  run_as_app "cd '$APP_DIR/gateway' && pnpm build"
}

ensure_postgres_running() {
  echo "[install] ensuring PostgreSQL is running..."
  if command_exists systemctl; then
    if ! sudo systemctl enable --now postgresql.service >/dev/null 2>&1; then
      echo "[install] ERROR: failed to start PostgreSQL service" >&2
      exit 20
    fi
  elif command_exists service; then
    if ! sudo service postgresql start >/dev/null 2>&1; then
      echo "[install] ERROR: failed to start PostgreSQL service" >&2
      exit 20
    fi
  fi

  for i in $(seq 1 30); do
    if sudo -u postgres pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
      echo "[install] PostgreSQL is ready"
      return 0
    fi
    echo "[install] waiting for PostgreSQL (${i}/30)..."
    sleep 1
  done

  echo "[install] ERROR: PostgreSQL did not become ready in time" >&2
  exit 21
}

apply_console_migrations() {
  echo "Applying console database migrations"
  run_as_app "cd '$APP_DIR/console' && pnpm prisma migrate deploy"

  if [[ "${SKIP_CONSOLE_SEED:-false}" != "true" ]]; then
    echo "Seeding console admin user (set SKIP_CONSOLE_SEED=true to skip)"
    run_as_app "cd '$APP_DIR/console' && pnpm seed"
  else
    echo "Skipping console seed per SKIP_CONSOLE_SEED=${SKIP_CONSOLE_SEED}"
  fi
}

parse_env_value() {
  local key="$1"
  [[ -f "$ENV_FILE" ]] || return 0

  while IFS= read -r line; do
    [[ -z "$line" || "${line#\#}" != "$line" || "$line" != *=* ]] && continue
    local name=${line%%=*}
    local value=${line#*=}
    if [[ "${name}" == "$key" ]]; then
      printf '%s\n' "$value"
      break
    fi
  done <"$ENV_FILE"
}

update_env_file() {
  local db_user=$1
  local db_pass=$2
  local db_name=$3
  local database_url="postgresql://${db_user}:${db_pass}@127.0.0.1:5432/${db_name}"

  declare -A updates=(
    [CONTROL_PORT]="${CONTROL_PORT}"
    [GATEWAY_PORT]="${GATEWAY_PORT}"
    [CONSOLE_PORT]="${CONSOLE_PORT}"
    [DATABASE_URL]="$database_url"
    [AION_CONTROL_POSTGRES_DSN]="$database_url"
    [AION_CONTROL_HTTP_HOST]="0.0.0.0"
    [AION_CONTROL_HTTP_PORT]="${CONTROL_PORT}"
    [AION_CONTROL_REDIS_URL]="redis://127.0.0.1:6379/0"
    [AION_REDIS_URL]="redis://127.0.0.1:6379/0"
    [AION_GATEWAY_HOST]="0.0.0.0"
    [AION_GATEWAY_PORT]="${GATEWAY_PORT}"
    [AION_CONTROL_GRPC]="localhost:50051"
    [AION_CONTROL_BASE]="http://localhost:${CONTROL_PORT}"
    [AION_CONTROL_CORS_ORIGINS]="http://localhost:${CONSOLE_PORT}"
    [AION_CORS_ORIGINS]="http://localhost:${CONSOLE_PORT}"
    [AION_CONSOLE_HEALTH_URL]="http://localhost:${CONSOLE_PORT}/health"
    [NEXTAUTH_URL]="http://localhost:${CONSOLE_PORT}"
    [NEXT_PUBLIC_GATEWAY_URL]="http://localhost:${GATEWAY_PORT}"
    [NEXT_PUBLIC_CONTROL_URL]="http://localhost:${CONTROL_PORT}"
    [NEXT_PUBLIC_CONTROL_BASE]="http://localhost:${CONTROL_PORT}"
  )

  [[ -f "$ENV_FILE" ]] || return 0

  local tmp
  tmp=$(mktemp)

  while IFS= read -r line; do
    if [[ -z "$line" || "${line#\#}" != "$line" || "$line" != *=* ]]; then
      printf '%s\n' "$line" >>"$tmp"
      continue
    fi

    local key=${line%%=*}
    if [[ -n "${updates[$key]:-}" ]]; then
      printf '%s=%s\n' "$key" "${updates[$key]}" >>"$tmp"
      unset 'updates[$key]'
    else
      printf '%s\n' "$line" >>"$tmp"
    fi
  done <"$ENV_FILE"

  for key in "${!updates[@]}"; do
    printf '%s=%s\n' "$key" "${updates[$key]}" >>"$tmp"
  done

  mv "$tmp" "$ENV_FILE"
  sudo chown "$APP_USER":"$APP_GROUP" "$ENV_FILE"
}

create_env_file() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "Creating environment file"
    run_as_app "cp '$APP_DIR/.env.example' '$ENV_FILE'"
  fi

  run_as_app "cd '$APP_DIR' && ln -sf ../.env gateway/.env"
  run_as_app "cd '$APP_DIR' && ln -sf ../.env console/.env"
}

configure_database() {
  echo "[install] configuring database"
  ensure_postgres_running

  local existing_url existing_user existing_pass existing_name
  existing_url=$(parse_env_value DATABASE_URL)

  if [[ $existing_url =~ ^postgresql://([^:/]+):([^@]+)@[^/]+/([^/?#]+) ]]; then
    existing_user=${BASH_REMATCH[1]}
    existing_pass=${BASH_REMATCH[2]}
    existing_name=${BASH_REMATCH[3]}
  else
    existing_user=""
    existing_pass=""
    existing_name=""
  fi

  local db_user=${DB_USER:-${existing_user:-aionos}}
  local db_pass=${DB_PASS:-${existing_pass:-aionos}}
  local db_name=${DB_NAME:-${existing_name:-omerta_db}}

  echo "Ensuring PostgreSQL role and database"
  sudo -u postgres psql \
    -v "db_user=${db_user}" \
    -v "db_pass=${db_pass}" \
    -v "db_name=${db_name}" <<'SQL'
SELECT
  set_config('aion.install.db_user', :'db_user', false),
  set_config('aion.install.db_pass', :'db_pass', false),
  set_config('aion.install.db_name', :'db_name', false);

DO $aion$
DECLARE
  v_db_user text := current_setting('aion.install.db_user');
  v_db_pass text := current_setting('aion.install.db_pass');
  v_db_name text := current_setting('aion.install.db_name');
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = v_db_user) THEN
    EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', v_db_user, v_db_pass);
  ELSE
    EXECUTE format('ALTER ROLE %I WITH LOGIN PASSWORD %L', v_db_user, v_db_pass);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = v_db_name) THEN
    EXECUTE format('CREATE DATABASE %I OWNER %I', v_db_name, v_db_user);
  ELSE
    EXECUTE format('ALTER DATABASE %I OWNER TO %I', v_db_name, v_db_user);
  END IF;

  EXECUTE format('GRANT ALL PRIVILEGES ON DATABASE %I TO %I', v_db_name, v_db_user);
END;
$aion$ LANGUAGE plpgsql;
SQL

  update_env_file "$db_user" "$db_pass" "$db_name"
}

run_migrations() {
  if [ -f "$APP_DIR/control/alembic.ini" ]; then
    echo "Running Alembic migrations"
    run_as_app "cd '$APP_DIR/control' && source '$APP_DIR/.venv/bin/activate' && alembic upgrade head"
  elif [ -f "$APP_DIR/control/manage.py" ]; then
    echo "Running Django migrations"
    run_as_app "cd '$APP_DIR/control' && source '$APP_DIR/.venv/bin/activate' && python manage.py migrate"
  else
    echo "No migrations configured - skipping"
  fi
}

install_systemd_units() {
  echo "[install] enabling and starting systemd services"
  if ! command_exists systemctl; then
    echo "systemctl not available; skipping service installation"
    return
  fi

  if ! sudo systemctl list-units >/dev/null 2>&1; then
    echo "systemd is not running; skipping service installation"
    return
  fi

  if [ ! -d "$SYSTEMD_DIR" ]; then
    echo "Systemd configuration directory missing at $SYSTEMD_DIR"
    return
  fi

  local console_log="/var/log/omerta-console.log"
  sudo touch "$console_log"
  sudo chown "$APP_USER":"$APP_GROUP" "$console_log"

  for unit in omerta-control.service omerta-gateway.service omerta-console.service; do
    if [ -f "$SYSTEMD_DIR/$unit" ]; then
      sudo install -m 644 "$SYSTEMD_DIR/$unit" "/etc/systemd/system/$unit"
    fi
  done

  sudo systemctl daemon-reload
  sudo systemctl enable --now omerta-control.service omerta-gateway.service omerta-console.service
  sudo systemctl restart omerta-control.service omerta-gateway.service omerta-console.service
}

self_check() {
  if [[ "${CI:-}" != "1" ]]; then
    return
  fi

  echo "[install] running CI health checks"
  local control_url="http://localhost:${CONTROL_PORT:-8000}/healthz"
  local gateway_url="http://localhost:${GATEWAY_PORT:-3000}/healthz"
  local console_url="http://localhost:${CONSOLE_PORT:-3001}/healthz"

  curl -fsS --max-time 10 "$control_url" >/dev/null
  curl -fsS --max-time 10 "$gateway_url" >/dev/null
  curl -fsS --max-time 10 "$console_url" >/dev/null
}

print_summary() {
  local control_port gateway_port console_port
  control_port=$(parse_env_value CONTROL_PORT)
  gateway_port=$(parse_env_value GATEWAY_PORT)
  console_port=$(parse_env_value CONSOLE_PORT)

  control_port=${control_port:-8000}
  gateway_port=${gateway_port:-3000}
  console_port=${console_port:-3001}

  cat <<MSG

Installation complete!

Services:
  Control : http://localhost:${control_port}
  Gateway : http://localhost:${gateway_port}
  Console : http://localhost:${console_port}

Manage services with:
  sudo systemctl status omerta-control omerta-gateway omerta-console
  sudo systemctl restart omerta-control omerta-gateway omerta-console

Smoke test:
  ${APP_DIR}/scripts/smoke.sh
MSG
}

main() {
  install_system_packages
  select_python_binary
  ensure_nodesource

  create_service_user
  clone_or_update_repo
  create_env_file
  configure_database
  provision_python
  provision_node_projects
  apply_console_migrations
  run_migrations
  install_systemd_units
  self_check
  print_summary
}

main "$@"
