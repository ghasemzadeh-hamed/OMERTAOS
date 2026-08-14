#!/usr/bin/env bash

native_die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

native_print_command() {
  printf 'DRY-RUN:'
  printf ' %q' "$@"
  printf '\n'
}

native_require_linux() {
  [[ "$(uname -s)" == Linux ]] || native_die 'Native service installation requires Linux'
}

native_prepare_runner() {
  id omertaos >/dev/null 2>&1 || native_die 'service account omertaos is missing; complete N2 first'
  [[ "$(id -u omertaos)" -ne 0 ]] || native_die 'omertaos must not be root'
  if ((EUID == 0)); then
    command -v runuser >/dev/null || native_die 'runuser is required when installer runs as root'
    NATIVE_SERVICE_PREFIX=(runuser -u omertaos -- env HOME=/var/lib/omertaos XDG_CACHE_HOME=/var/lib/omertaos/cache)
  elif [[ "$(id -un)" == omertaos ]]; then
    NATIVE_SERVICE_PREFIX=(env HOME=/var/lib/omertaos XDG_CACHE_HOME=/var/lib/omertaos/cache)
  else
    native_die 'run as root or the omertaos service account'
  fi
}

native_run_service() {
  if "$DRY_RUN"; then native_print_command "${NATIVE_SERVICE_PREFIX[@]}" "$@"; else "${NATIVE_SERVICE_PREFIX[@]}" "$@"; fi
}

native_prepare_dir() {
  local path="$1" mode="${2:-0750}"
  if "$DRY_RUN"; then
    if ((EUID == 0)); then native_print_command install -d -o omertaos -g omertaos -m "$mode" "$path"
    else native_print_command install -d -m "$mode" "$path"; fi
  elif ((EUID == 0)); then install -d -o omertaos -g omertaos -m "$mode" "$path"
  else install -d -m "$mode" "$path"
  fi
}

native_assert_service_writable() {
  local path="$1"
  "$DRY_RUN" && return 0
  if ((EUID == 0)); then
    runuser -u omertaos -- test -w "$path" || native_die "omertaos cannot write build directory: $path"
  else
    [[ -w "$path" ]] || native_die "omertaos cannot write build directory: $path"
  fi
}

native_require_node() {
  command -v node >/dev/null || native_die 'node is required; complete N2 first'
  command -v npm >/dev/null || native_die 'npm is required; complete N2 first'
  local major
  major="$(node -p 'Number(process.versions.node.split(".")[0])')"
  [[ "$major" == 22 ]] || native_die "Node.js $(node --version) violates the N1 Node 22 contract"
}

native_load_env_file() {
  local path="$1" destination_name="$2" line key value
  [[ -r "$path" ]] || native_die "environment file is not readable: $path"
  declare -n destination="$destination_name"
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "$line" || "$line" == \#* ]] && continue
    [[ "$line" =~ ^[A-Z][A-Z0-9_]*=.*$ ]] || native_die "$path contains an invalid assignment"
    key="${line%%=*}"
    value="${line#*=}"
    [[ ! -v "destination[$key]" ]] || native_die "$path contains duplicate key: $key"
    destination["$key"]="$value"
  done < "$path"
}
