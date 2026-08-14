#!/usr/bin/env bash
set -euo pipefail

: "${OMERTAOS_COMMIT_SHA:?OMERTAOS_COMMIT_SHA is required}"
[[ "$OMERTAOS_COMMIT_SHA" =~ ^[0-9a-f]{40}$ ]] || {
  echo 'OMERTAOS_COMMIT_SHA must be a full Git SHA' >&2
  exit 1
}

public_key="$(tr -d '\r\n' </run/n0/authorized_key)"
[[ "$public_key" =~ ^ssh-(ed25519|rsa)[[:space:]] ]] || {
  echo 'N0 SSH public key is invalid' >&2
  exit 1
}

install -d -m 0700 -o omerta -g omerta /home/omerta/.ssh
printf '%s\n' "$public_key" >/home/omerta/.ssh/authorized_keys
chown omerta:omerta /home/omerta/.ssh/authorized_keys
chmod 0600 /home/omerta/.ssh/authorized_keys
install -d -m 0750 -o root -g root /etc/omertaos

actual_sha="$(git -c safe.directory=/srv/omertaos-source -C /srv/omertaos-source rev-parse HEAD)"
[[ "$actual_sha" == "$OMERTAOS_COMMIT_SHA" ]] || {
  echo "Release SHA mismatch: expected $OMERTAOS_COMMIT_SHA, got $actual_sha" >&2
  exit 1
}
[[ -z "$(git -c safe.directory=/srv/omertaos-source -C /srv/omertaos-source status --porcelain)" ]] || {
  echo 'Mounted release snapshot is not clean' >&2
  exit 1
}

printf '%s\n' "$actual_sha" >/var/lib/omertaos-n0/release-commit
date --iso-8601=seconds >/var/lib/omertaos-n0/ready
install -d -m 0755 -o root -g root /run/sshd
/usr/sbin/sshd -t
