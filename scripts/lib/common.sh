#!/usr/bin/env bash
# Common helper functions for installation scripts.

log_info() {
  printf '[INFO] %s\n' "$*"
}

log_warn() {
  printf '[WARN] %s\n' "$*" >&2
}

log_error() {
  printf '[ERROR] %s\n' "$*" >&2
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

require_command() {
  local name=$1
  local hint=${2:-}
  if ! command_exists "$name"; then
    if [[ -n "$hint" ]]; then
      log_error "Required command '$name' not found. $hint"
    else
      log_error "Required command '$name' not found."
    fi
    return 1
  fi
}

confirm_directory() {
  local path=$1
  if [[ ! -d "$path" ]]; then
    log_error "Expected directory '$path' was not found."
    return 1
  fi
}

