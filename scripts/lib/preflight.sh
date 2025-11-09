#!/usr/bin/env bash
# shellcheck shell=bash

run_preflight() {
  local root_dir=$1
  local noninteractive_flag=$2
  local preflight="${root_dir}/tools/preflight.sh"

  if [[ ! -x "${preflight}" ]]; then
    return
  fi

  log_info "Running preflight checks"
  local args=()
  if [[ "${noninteractive_flag}" == "true" ]]; then
    args+=(--noninteractive)
  fi

  if ! "${preflight}" "${args[@]}"; then
    log_warn "Preflight reported issues"
  fi
}
