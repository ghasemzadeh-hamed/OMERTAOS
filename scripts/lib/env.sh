#!/usr/bin/env bash
# shellcheck shell=bash

# Functions for environment file management used by QuickSetup.

ensure_env_file() {
  local root_dir=$1
  local env_file="${root_dir}/.env"
  local template_candidates=(
    "${root_dir}/.env.example"
    "${root_dir}/config/templates/.env.example"
    "${root_dir}/config/.env.example"
  )

  if [[ -f "${env_file}" ]]; then
    return
  fi

  local template=""
  for candidate in "${template_candidates[@]}"; do
    if [[ -f "${candidate}" ]]; then
      template="${candidate}"
      break
    fi
  done

  if [[ -n "${template}" ]]; then
    local relative_template="${template#${root_dir}/}"
    log_info "Creating .env from template ${relative_template}"
    cp "${template}" "${env_file}"
  else
    log_warn "No .env template found; creating empty .env"
    : >"${env_file}"
  fi
}

update_env_profile() {
  local root_dir=$1
  local profile=$2
  local telemetry_raw=$3
  local telemetry_endpoint=$4
  local policy_dir=$5
  local volume_root=$6

  local env_file="${root_dir}/.env"

  python3 - <<PY
from pathlib import Path

env_path = Path(${env_file!r})
if not env_path.exists():
    raise SystemExit(0)

lines = [line.rstrip("\n") for line in env_path.read_text().splitlines()]

def keep_line(raw: str) -> bool:
    if not raw or raw.lstrip().startswith('#') or '=' not in raw:
        return True
    key, _ = raw.split('=', 1)
    return key not in {
        "AION_PROFILE",
        "FEATURE_SEAL",
        "AION_TELEMETRY_OPT_IN",
        "AION_TELEMETRY_ENDPOINT",
        "AION_POLICY_DIR",
        "AION_VOLUME_ROOT",
    }

filtered = [line for line in lines if keep_line(line)]

profile = ${profile!r}
feature_seal = '1' if profile == 'enterprise-vip' else '0'
telemetry_raw = ${telemetry_raw!r}
telemetry_value = str(telemetry_raw).lower() in {'1', 'true', 'y', 'yes', 'on'}
telemetry_endpoint = ${telemetry_endpoint!r}
policy_dir = ${policy_dir!r}
volume_root = ${volume_root!r}

filtered.extend([
    f"AION_PROFILE={profile}",
    f"FEATURE_SEAL={feature_seal}",
    f"AION_TELEMETRY_OPT_IN={'true' if telemetry_value else 'false'}",
    f"AION_TELEMETRY_ENDPOINT={telemetry_endpoint}",
    f"AION_POLICY_DIR={policy_dir}",
    f"AION_VOLUME_ROOT={volume_root}",
])

env_path.write_text("\n".join(filtered) + "\n")
PY
}

write_profile_metadata() {
  local root_dir=$1
  local profile=$2
  local metadata_dir="${root_dir}/.aionos"

  mkdir -p "${metadata_dir}"

  python3 - <<PY
from pathlib import Path
from datetime import datetime
import json

metadata_dir = Path(${metadata_dir!r})
metadata_dir.mkdir(parents=True, exist_ok=True)
profile_file = metadata_dir / "profile.json"
data = {
    "profile": ${profile!r},
    "setupDone": True,
    "updatedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
}
profile_file.write_text(json.dumps(data, indent=2) + "\n")
PY
}
