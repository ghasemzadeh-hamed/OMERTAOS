#!/usr/bin/env bash
# shellcheck shell=bash

# Utilities for generating ephemeral bootstrap certificates when Vault is not
# yet available. Certificates are placed under config/certs/bootstrap/ and are
# intentionally short-lived.

_read_env_file_var() {
  local env_file=$1
  local key=$2
  if [[ -f "${env_file}" ]]; then
    local line
    line=$(grep -E "^${key}=" "${env_file}" | tail -n1 || true)
    if [[ -n "${line}" ]]; then
      echo "${line#*=}"
    fi
  fi
}

ensure_ephemeral_certs() {
  local root_dir=$1
  local env_file="${root_dir}/.env"
  local vault_enabled_raw=${VAULT_ENABLED:-}

  if [[ -z "${vault_enabled_raw}" ]]; then
    vault_enabled_raw=$(_read_env_file_var "${env_file}" "VAULT_ENABLED")
  fi

  if [[ "$(normalize_boolean "${vault_enabled_raw}")" == "true" ]]; then
    log_info "Vault is enabled; skipping bootstrap certificate generation."
    return 0
  fi

  require_command openssl "Install OpenSSL from https://www.openssl.org/" || return 1

  local cert_root="${root_dir}/config/certs"
  local bootstrap_dir="${cert_root}/bootstrap"
  ensure_directory "${cert_root}"
  ensure_directory "${bootstrap_dir}"

  local marker="${bootstrap_dir}/.generated"
  if [[ -f "${marker}" ]]; then
    log_info "Bootstrap certificates already exist at ${bootstrap_dir}."
    return 0
  fi

  local days=${AION_BOOTSTRAP_CERT_DAYS:-3}
  local ca_key="${bootstrap_dir}/bootstrap-ca-key.pem"
  local ca_cert="${bootstrap_dir}/bootstrap-ca.pem"
  local server_key="${bootstrap_dir}/control-server-key.pem"
  local server_cert="${bootstrap_dir}/control-server.pem"
  local client_key="${bootstrap_dir}/gateway-client-key.pem"
  local client_cert="${bootstrap_dir}/gateway-client.pem"
  local serial_file="${bootstrap_dir}/bootstrap-ca.srl"

  log_info "Generating ephemeral bootstrap certificate authority (${days} day validity)."

  openssl req -x509 -newkey rsa:4096 -nodes -sha256 \
    -subj "/CN=AIONOS Bootstrap CA" \
    -keyout "${ca_key}" \
    -out "${ca_cert}" \
    -days "${days}" >/dev/null 2>&1

  local san_config
  san_config=$(mktemp)
  cat >"${san_config}" <<SAN
subjectAltName=DNS:localhost,IP:127.0.0.1
keyUsage=digitalSignature,keyEncipherment
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:false
extendedKeyUsage=serverAuth,clientAuth
SAN

  log_info "Issuing control-plane server certificate from bootstrap CA."
  openssl req -new -newkey rsa:4096 -nodes -sha256 \
    -subj "/CN=control.local" \
    -keyout "${server_key}" \
    -out "${server_key%.pem}.csr" >/dev/null 2>&1
  openssl x509 -req -sha256 \
    -in "${server_key%.pem}.csr" \
    -CA "${ca_cert}" -CAkey "${ca_key}" -CAcreateserial -CAserial "${serial_file}" \
    -out "${server_cert}" -days "${days}" \
    -extfile "${san_config}" >/dev/null 2>&1

  log_info "Issuing gateway client certificate from bootstrap CA."
  openssl req -new -newkey rsa:4096 -nodes -sha256 \
    -subj "/CN=gateway.local" \
    -keyout "${client_key}" \
    -out "${client_key%.pem}.csr" >/dev/null 2>&1
  openssl x509 -req -sha256 \
    -in "${client_key%.pem}.csr" \
    -CA "${ca_cert}" -CAkey "${ca_key}" -CAserial "${serial_file}" \
    -out "${client_cert}" -days "${days}" \
    -extfile "${san_config}" >/dev/null 2>&1

  rm -f "${server_key%.pem}.csr" "${client_key%.pem}.csr" "${san_config}" "${serial_file}"

  {
    printf 'generated_at=%s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf 'valid_days=%s\n' "${days}"
  } >"${marker}"

  log_info "Ephemeral certificates written to ${bootstrap_dir}. Replace them once Vault is initialised."
}
