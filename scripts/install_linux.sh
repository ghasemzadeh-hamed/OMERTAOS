#!/usr/bin/env bash
set -euo pipefail

APP_ROOT=${APP_ROOT:-/opt/omerta}
APP_USER=${APP_USER:-omerta}
APP_GROUP=${APP_GROUP:-www-data}
REPO=${REPO:-https://github.com/Hamedghz/OMERTAOS.git}
APP_DIR="$APP_ROOT/OMERTAOS"
ENV_FILE="$APP_DIR/.env"
SYSTEMD_DIR="$APP_DIR/configs/systemd"
NODE_REQUIRED_MAJOR=18

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
  sudo mkdir -p "$APP_ROOT"
  sudo chown "$APP_USER":"$APP_GROUP" "$APP_ROOT"

  if [ ! -d "$APP_DIR/.git" ]; then
    echo "Cloning repository into $APP_DIR"
    run_as_app "git clone '$REPO' '$APP_DIR'"
  else
    echo "Updating existing repository in $APP_DIR"
    run_as_app "cd '$APP_DIR' && git pull --ff-only"
  fi

  sudo chown -R "$APP_USER":"$APP_GROUP" "$APP_DIR"
}

provision_python() {
  if [ ! -d "$APP_DIR/.venv" ]; then
    echo "Creating Python virtual environment"
    run_as_app "python3.11 -m venv '$APP_DIR/.venv'"
  fi

  echo "Installing Python dependencies"
  run_as_app "cd '$APP_DIR/control' && source '$APP_DIR/.venv/bin/activate' && pip install --upgrade pip wheel setuptools && pip install ."
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
    run_as_app "cd '$APP_DIR/$project' && pnpm install --frozen-lockfile"
  done

  echo "Building console"
  run_as_app "cd '$APP_DIR/console' && pnpm build"

  echo "Building gateway"
  run_as_app "cd '$APP_DIR/gateway' && pnpm build"
}

parse_env_value() {
  local key=$1
  python3 - <<PY
from pathlib import Path
import sys
path = Path("$ENV_FILE")
if not path.exists():
    sys.exit(0)
for raw in path.read_text().splitlines():
    if not raw or raw.startswith('#') or '=' not in raw:
        continue
    name, value = raw.split('=', 1)
    if name.strip() == "$key":
        print(value.strip())
        break
PY
}

update_env_file() {
  local db_user=$1
  local db_pass=$2
  local db_name=$3
  local database_url="postgresql://${db_user}:${db_pass}@127.0.0.1:5432/${db_name}"

  python3 - <<PY
from pathlib import Path

path = Path("$ENV_FILE")
if not path.exists():
    raise SystemExit(0)

updates = {
    "DATABASE_URL": "$database_url",
    "AION_CONTROL_POSTGRES_DSN": "$database_url",
    "AION_DB_USER": "$db_user",
    "AION_DB_PASSWORD": "$db_pass",
    "AION_DB_NAME": "$db_name",
}

lines = path.read_text().splitlines()
keys = set(updates)

for idx, line in enumerate(lines):
    if not line or line.lstrip().startswith('#') or '=' not in line:
        continue
    key, _ = line.split('=', 1)
    key = key.strip()
    if key in updates:
        lines[idx] = f"{key}={updates[key]}"
        keys.discard(key)

for key in sorted(keys):
    lines.append(f"{key}={updates[key]}")

path.write_text("\n".join(lines) + "\n")
PY
}

create_env_file() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "Creating environment file"
    run_as_app "cp '$APP_DIR/.env.example' '$ENV_FILE'"
  fi

  run_as_app "cd '$APP_DIR' && ln -sf ../.env gateway/.env"
  run_as_app "cd '$APP_DIR' && ln -sf ../.env console/.env"
}

random_password() {
  tr -dc 'A-Za-z0-9' </dev/urandom | head -c 24
}

configure_database() {
  local existing_user existing_pass existing_name
  existing_user=$(parse_env_value DATABASE_URL | python3 - <<'PY'
import sys
from urllib.parse import urlparse
value = sys.stdin.read().strip()
if not value:
    print("", "", "", sep="\n")
else:
    parsed = urlparse(value)
    name = parsed.path[1:] if parsed.path.startswith('/') else parsed.path
    print(parsed.username or "")
    print(parsed.password or "")
    print(name or "")
PY
)

  IFS=$'\n' read -r existing_user existing_pass existing_name <<<"$existing_user"

  local db_user=${DB_USER:-${existing_user:-omerta}}
  local db_pass=${DB_PASS:-${existing_pass:-}};
  local db_name=${DB_NAME:-${existing_name:-omerta_db}}

  if [ -z "$db_pass" ]; then
    db_pass=$(random_password)
  fi

  echo "Ensuring PostgreSQL role $db_user"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='${db_user}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER ${db_user} WITH PASSWORD '${db_pass}';"

  echo "Ensuring database $db_name"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${db_name}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE ${db_name} OWNER ${db_user};"

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

  for unit in omerta-control.service omerta-gateway.service omerta-console.service; do
    if [ -f "$SYSTEMD_DIR/$unit" ]; then
      sudo install -m 644 "$SYSTEMD_DIR/$unit" "/etc/systemd/system/$unit"
    fi
  done

  sudo systemctl daemon-reload
  sudo systemctl enable --now omerta-control.service omerta-gateway.service omerta-console.service
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
  sudo apt update -y
  sudo apt install -y git curl ca-certificates build-essential python3.11 python3.11-venv python3.11-dev \
    redis-server postgresql postgresql-contrib

  ensure_nodesource

  create_service_user
  clone_or_update_repo
  create_env_file
  configure_database
  provision_python
  provision_node_projects
  run_migrations
  install_systemd_units
  print_summary
}

main "$@"
