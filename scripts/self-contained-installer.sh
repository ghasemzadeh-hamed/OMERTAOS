#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "[ERROR] Please run as root (sudo)." >&2
  exit 1
fi

INSTALL_ROOT="${INSTALL_ROOT:-/opt/platform}"
GIT_REPO_URL="${GIT_REPO_URL:-https://github.com/Hamedghz/OMERTAOS.git}"
GIT_REPO_BRANCH="${GIT_REPO_BRANCH:-main}"
PLATFORM_USER_DEFAULT="${PLATFORM_USER_DEFAULT:-platform}"
PLATFORM_GROUP_DEFAULT="${PLATFORM_GROUP_DEFAULT:-platform}"
AUTOSTART_APPS_DEFAULT="xfce4-terminal"
NONINTERACTIVE="${NONINTERACTIVE:-false}"

log() { echo "[installer] $*"; }
warn() { echo "[installer][warn] $*"; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || return 1
}

rand_b64() {
  local bytes="${1:-32}"
  openssl rand -base64 "$bytes" | tr -d '\n'
}

prompt_value() {
  local var_name="$1" prompt="$2" default_value="$3" secret="${4:-false}"
  local current="${!var_name:-}"
  if [[ -n "$current" ]]; then
    return 0
  fi

  if [[ "$NONINTERACTIVE" == "true" ]]; then
    printf -v "$var_name" '%s' "$default_value"
    return 0
  fi

  local input
  if [[ "$secret" == "true" ]]; then
    read -r -s -p "$prompt [$default_value]: " input || true
    echo
  else
    read -r -p "$prompt [$default_value]: " input || true
  fi
  input="${input:-$default_value}"
  printf -v "$var_name" '%s' "$input"
}

install_apt_packages() {
  export DEBIAN_FRONTEND=noninteractive
  log "Installing required system packages..."
  apt-get update -y
  apt-get install -y --no-install-recommends \
    ca-certificates curl git jq sudo openssl \
    python3 python3-venv python3-pip \
    xfce4 xfce4-terminal lightdm dbus-x11 xauth \
    xpra \
    lxc lxc-utils uidmap bridge-utils \
    cloud-image-utils qemu-utils
}

clone_or_update_repo() {
  local parent_dir
  parent_dir="$(dirname "$INSTALL_ROOT")"
  mkdir -p "$parent_dir"

  if [[ ! -d "$INSTALL_ROOT/.git" ]]; then
    log "Cloning repository to $INSTALL_ROOT"
    git clone --branch "$GIT_REPO_BRANCH" "$GIT_REPO_URL" "$INSTALL_ROOT"
  else
    log "Repository already exists, updating..."
    git -C "$INSTALL_ROOT" fetch --all --prune
    git -C "$INSTALL_ROOT" checkout "$GIT_REPO_BRANCH"
    git -C "$INSTALL_ROOT" pull --ff-only origin "$GIT_REPO_BRANCH"
  fi
}

install_python_dependencies() {
  if [[ ! -f "$INSTALL_ROOT/requirements.txt" ]]; then
    warn "requirements.txt not found in repo, skipping pip install"
    return 0
  fi

  log "Installing Python dependencies from repository requirements.txt"
  python3 -m venv "$INSTALL_ROOT/.venv"
  "$INSTALL_ROOT/.venv/bin/pip" install --upgrade pip wheel setuptools
  "$INSTALL_ROOT/.venv/bin/pip" install -r "$INSTALL_ROOT/requirements.txt"
}

ensure_group_user() {
  if ! getent group "$PLATFORM_GROUP" >/dev/null; then
    log "Creating group: $PLATFORM_GROUP"
    groupadd "$PLATFORM_GROUP"
  fi

  if ! id -u "$PLATFORM_USER" >/dev/null 2>&1; then
    log "Creating user: $PLATFORM_USER"
    useradd -m -s /bin/bash -g "$PLATFORM_GROUP" "$PLATFORM_USER"
  fi

  echo "$PLATFORM_USER:$PLATFORM_PASSWORD" | chpasswd
  usermod -aG sudo,lxd "$PLATFORM_USER"
  chown -R "$PLATFORM_USER:$PLATFORM_GROUP" "$INSTALL_ROOT"
}

configure_lightdm_autologin() {
  local lightdm_conf="/etc/lightdm/lightdm.conf"
  mkdir -p /etc/lightdm
  if [[ ! -f "$lightdm_conf" ]]; then
    cat > "$lightdm_conf" <<'CONF'
[Seat:*]
CONF
  fi

  if ! grep -q '^autologin-user=' "$lightdm_conf"; then
    printf '\nautologin-user=%s\n' "$PLATFORM_USER" >> "$lightdm_conf"
  else
    sed -i "s/^autologin-user=.*/autologin-user=${PLATFORM_USER}/" "$lightdm_conf"
  fi

  if ! grep -q '^autologin-user-timeout=' "$lightdm_conf"; then
    echo 'autologin-user-timeout=0' >> "$lightdm_conf"
  else
    sed -i 's/^autologin-user-timeout=.*/autologin-user-timeout=0/' "$lightdm_conf"
  fi

  systemctl enable lightdm >/dev/null 2>&1 || warn "Could not enable lightdm right now"
}

configure_xpra() {
  install -d -m 0755 /etc/systemd/system
  cat > /etc/systemd/system/xpra-platform.service <<SERVICE
[Unit]
Description=Platform browser-accessible GUI (Xpra)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${PLATFORM_USER}
Group=${PLATFORM_GROUP}
Environment=HOME=/home/${PLATFORM_USER}
ExecStart=/usr/bin/xpra start :100 --bind-tcp=0.0.0.0:14500 --html=on --daemon=no --start=xfce4-session --exit-with-children=yes
ExecStop=/usr/bin/xpra stop :100
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

  systemctl daemon-reload
  systemctl enable --now xpra-platform.service
}

configure_security_materials() {
  local sec_dir="/etc/platform/security"
  install -d -m 0700 "$sec_dir"

  [[ -f "$sec_dir/platform.key" ]] || openssl genrsa -out "$sec_dir/platform.key" 2048
  [[ -f "$sec_dir/platform.crt" ]] || openssl req -new -x509 -key "$sec_dir/platform.key" -out "$sec_dir/platform.crt" -days 3650 -subj "/CN=platform.local"
  [[ -f "$sec_dir/runtime_token" ]] || rand_b64 48 > "$sec_dir/runtime_token"
  [[ -f "$sec_dir/db_password" ]] || rand_b64 24 > "$sec_dir/db_password"

  chmod 0600 "$sec_dir"/*
}

configure_platform_autostart() {
  local autostart_dir="/home/${PLATFORM_USER}/.config/autostart"
  install -d -o "$PLATFORM_USER" -g "$PLATFORM_GROUP" "$autostart_dir"

  cat > "$autostart_dir/platform-terminal.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Platform Terminal
Exec=xfce4-terminal --working-directory=${INSTALL_ROOT}
X-GNOME-Autostart-enabled=true
DESKTOP

  cat > "$autostart_dir/platform-config.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Platform Config
Exec=xfce4-terminal -e \"bash -lc '${INSTALL_ROOT}/scripts/quicksetup.sh --noninteractive || bash'\"
X-GNOME-Autostart-enabled=true
DESKTOP

  chown -R "$PLATFORM_USER:$PLATFORM_GROUP" "/home/${PLATFORM_USER}/.config"
}

configure_lxc_ephemeral_runtime() {
  local sandbox_dir="/opt/platform-sandbox"
  local runner="/usr/local/bin/platform-sandbox-runner"
  install -d -m 0755 "$sandbox_dir"

  cat > "$runner" <<'RUNNER'
#!/usr/bin/env bash
set -Eeuo pipefail

BASE_NAME="ai-base"
RUNTIME_NAME="ai-runtime"
TEMPLATE="download"
DIST="ubuntu"
RELEASE="noble"
ARCH="amd64"

if lxc-info -n "$RUNTIME_NAME" >/dev/null 2>&1; then
  lxc-stop -n "$RUNTIME_NAME" >/dev/null 2>&1 || true
  lxc-destroy -n "$RUNTIME_NAME" >/dev/null 2>&1 || true
fi

if ! lxc-info -n "$BASE_NAME" >/dev/null 2>&1; then
  lxc-create -n "$BASE_NAME" -t "$TEMPLATE" -- -d "$DIST" -r "$RELEASE" -a "$ARCH"
fi

lxc-copy -n "$BASE_NAME" -N "$RUNTIME_NAME" -e
lxc-start -n "$RUNTIME_NAME" -d
RUNNER

  chmod +x "$runner"

  cat > /etc/systemd/system/platform-sandbox.service <<SERVICE
[Unit]
Description=Ephemeral AI runtime sandbox (LXC)
After=network-online.target lxc.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=${runner}
ExecStop=/usr/bin/lxc-stop -n ai-runtime
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
SERVICE

  systemctl daemon-reload
  systemctl enable --now platform-sandbox.service
}

main() {
  prompt_value PLATFORM_USER "Enter GUI username" "$PLATFORM_USER_DEFAULT"
  prompt_value PLATFORM_PASSWORD "Enter GUI password" "$(rand_b64 12)" true
  prompt_value PLATFORM_GROUP "Enter primary group" "$PLATFORM_GROUP_DEFAULT"

  log "Starting self-contained platform bootstrap"
  install_apt_packages
  clone_or_update_repo
  install_python_dependencies
  ensure_group_user
  configure_lightdm_autologin
  configure_xpra
  configure_security_materials
  configure_platform_autostart
  configure_lxc_ephemeral_runtime

  log "Completed successfully."
  log "Xpra URL: http://<server-ip>:14500/"
  log "GUI user: ${PLATFORM_USER}"
}

main "$@"
