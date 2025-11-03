#!/usr/bin/env bash
set -euo pipefail

ARCHIVE=${1:?"usage: restore.sh <archive>"}
if [ ! -f "$ARCHIVE" ]; then
  echo "archive not found: $ARCHIVE" >&2
  exit 1
fi
TMP_DIR=$(mktemp -d)
tar -xzf "$ARCHIVE" -C "$TMP_DIR"
rsync -a "$TMP_DIR"/ ./
rm -rf "$TMP_DIR"
printf 'restore completed from %s\n' "$ARCHIVE"
