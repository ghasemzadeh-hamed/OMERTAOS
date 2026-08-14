#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
CHECK_ONLY=false
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
UNIT_SOURCE="$(cd -- "$SCRIPT_DIR/../systemd" && pwd)"
UNIT_DEST=/etc/systemd/system

usage() {
  cat <<'EOF'
Usage: install-systemd.sh [--dry-run|--check] [--help]

Verify and install the six canonical Native systemd assets, reload systemd, and
enable only omertaos.target. Services are never started by this command.
--check is read-only and verifies installed units, environment permissions, and
the enabled target.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
run() {
  if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "$@"; printf '\n'
  else "$@"; fi
}

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --check) CHECK_ONLY=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done
"$DRY_RUN" && "$CHECK_ONLY" && die '--dry-run and --check are mutually exclusive'

[[ "$(uname -s)" == Linux ]] || die 'systemd setup requires Linux'
[[ -d /run/systemd/system ]] || die 'systemd must be running on the Native target'
for executable in systemctl systemd-analyze install stat cmp id python3 grep; do
  command -v "$executable" >/dev/null || die "missing required executable: $executable"
done
if ((EUID == 0)); then PRIV=(); else command -v sudo >/dev/null || die 'run as root or install sudo'; PRIV=(sudo); fi
id omertaos >/dev/null 2>&1 || die 'service account omertaos is missing; complete N2 first'
[[ "$(id -u omertaos)" -ne 0 ]] || die 'omertaos must not be root'
[[ -x /usr/bin/node ]] || die '/usr/bin/node is required by the Node service units'

declare -A EXPECTED_MODES=(
  [omertaos.env]=644
  [runtime.env]=640
  [control.env]=640
  [gateway.env]=640
  [console.env]=640
  [installer.env]=600
)
for name in "${!EXPECTED_MODES[@]}"; do
  path="/etc/omertaos/$name"
  [[ -f "$path" ]] || die "missing environment file: $path"
  [[ "$(stat -c '%U' "$path")" == root ]] || die "$path must be owned by root"
  [[ "$(stat -c '%a' "$path")" == "${EXPECTED_MODES[$name]}" ]] || die "$path must have mode ${EXPECTED_MODES[$name]}"
  assignments="$(grep -Ev '^[[:space:]]*(#|$)' "$path" || true)"
  grep -Eq 'CHANGE_ME|REPLACE_ME|<REQUIRED>' <<< "$assignments" && die "$path contains a placeholder"
  grep -Eq '\$\{|\$\(|`' <<< "$assignments" && die "$path contains forbidden shell expansion"
done
for name in runtime.env control.env gateway.env console.env; do
  [[ "$(stat -c '%G' "/etc/omertaos/$name")" == omertaos ]] || die "/etc/omertaos/$name must use group omertaos"
done
for name in omertaos.env installer.env; do
  [[ "$(stat -c '%G' "/etc/omertaos/$name")" == root ]] || die "/etc/omertaos/$name must use group root"
done
python3 "$SCRIPT_DIR/../env/validate_data_env.py" \
  --installer /etc/omertaos/installer.env \
  --control /etc/omertaos/control.env \
  --console /etc/omertaos/console.env

[[ -L /opt/omertaos/current ]] || die 'active release symlink is missing; prepare N8 release activation first'
[[ -x /opt/omertaos/current/bin/runtime-daemon ]] || die 'Runtime binary is missing from active release'
[[ -x /opt/omertaos/current/.venv/control/bin/python ]] || die 'Control virtualenv is missing from active release'
[[ -f /opt/omertaos/current/gateway/dist/server.js ]] || die 'Gateway artifact is missing from active release'
[[ -f /opt/omertaos/current/console/.next/BUILD_ID ]] || die 'Console artifact is missing from active release'

units=(
  omertaos-install.service
  omertaos-runtime.service
  omertaos-control.service
  omertaos-gateway.service
  omertaos-console.service
  omertaos.target
)
unit_paths=()
for unit in "${units[@]}"; do
  [[ -f "$UNIT_SOURCE/$unit" ]] || die "missing unit source: $unit"
  unit_paths+=("$UNIT_SOURCE/$unit")
done
systemd-analyze verify "${unit_paths[@]}"

if "$CHECK_ONLY"; then
  for unit in "${units[@]}"; do
    [[ -f "$UNIT_DEST/$unit" ]] || die "installed unit is missing: $unit"
    cmp -s "$UNIT_SOURCE/$unit" "$UNIT_DEST/$unit" || die "installed unit differs from canonical source: $unit"
  done
  systemctl is-enabled --quiet omertaos.target || die 'omertaos.target is not enabled'
  if systemctl is-active --quiet omertaos.target; then
    printf 'N6 systemd check passed; omertaos.target is currently active.\n'
  else
    printf 'N6 systemd check passed; omertaos.target is installed and enabled but not active.\n'
  fi
  exit 0
fi

run "${PRIV[@]}" install -d -o omertaos -g omertaos -m 0750 /var/lib/omertaos/runtime /var/lib/omertaos/control
run "${PRIV[@]}" install -d -o omertaos -g omertaos -m 0750 /etc/omertaos/secrets/control
for unit in "${units[@]}"; do
  run "${PRIV[@]}" install -o root -g root -m 0644 "$UNIT_SOURCE/$unit" "$UNIT_DEST/$unit"
done
run "${PRIV[@]}" systemctl daemon-reload
run "${PRIV[@]}" systemctl enable omertaos.target
printf 'N6 systemd units installed and target enabled; no service was started.\n'
