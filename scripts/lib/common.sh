#!/usr/bin/env bash
# Common helper functions for installation scripts.

# shellcheck shell=bash

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

ensure_directory() {
  local dir=$1
  if [[ -z "$dir" ]]; then
    log_error "ensure_directory requires a directory path"
    return 1
  fi
  if [[ ! -d "$dir" ]]; then
    mkdir -p "$dir"
    log_info "Created directory: $dir"
  fi
}

normalize_boolean() {
  local raw=${1:-}
  case "${raw,,}" in
    1|true|yes|y|on) echo "true" ;;
    0|false|no|n|off|"") echo "false" ;;
    *)
      log_warn "Unrecognized boolean value '${raw}'. Defaulting to false."
      echo "false"
      ;;
  esac
}

