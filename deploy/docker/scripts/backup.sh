#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR=${1:-backups}
mkdir -p "$TARGET_DIR"
timestamp=$(date +%Y%m%d%H%M%S)
archive="$TARGET_DIR/aion-backup-$timestamp.tar.gz"
tar -czf "$archive" artifacts policies configs
printf 'backup created at %s\n' "$archive"
