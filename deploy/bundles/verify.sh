#!/usr/bin/env bash
set -euo pipefail

BUNDLE_ROOT=${1:-$(dirname "$0")}
EXIT_CODE=0

log() {
  printf '%s\n' "$1"
}

verify_bundle() {
  local bundle_dir="$1"
  if [[ ! -f "$bundle_dir/VERSION" ]]; then
    log "[ERROR] Missing VERSION file in $bundle_dir"
    EXIT_CODE=1
    return
  fi
  local version
  version=$(<"$bundle_dir/VERSION")
  if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
    log "[ERROR] Invalid semantic version '$version' in $bundle_dir/VERSION"
    EXIT_CODE=1
  fi

  local checksum_file="$bundle_dir/CHECKSUMS.txt"
  if [[ ! -f "$checksum_file" ]]; then
    log "[ERROR] Missing CHECKSUMS.txt in $bundle_dir"
    EXIT_CODE=1
    return
  fi

  while read -r sha path || [[ -n "$sha" ]]; do
    [[ -z "$sha" || "$sha" == \#* ]] && continue
    if [[ -z "$path" ]]; then
      log "[ERROR] Malformed line in $checksum_file: '$sha'"
      EXIT_CODE=1
      continue
    fi
    local absolute_path="$bundle_dir/$path"
    if [[ ! -f "$absolute_path" ]]; then
      log "[ERROR] Listed artifact '$path' not found in $bundle_dir"
      EXIT_CODE=1
      continue
    fi
    local computed
    computed=$(sha256sum "$absolute_path" | awk '{print $1}')
    if [[ "$computed" != "$sha" ]]; then
      log "[ERROR] Checksum mismatch for $path (expected $sha, got $computed)"
      EXIT_CODE=1
    else
      log "[OK] $path checksum verified"
    fi
  done <"$checksum_file"
}

for bundle in "$BUNDLE_ROOT"/*; do
  [[ -d "$bundle" ]] || continue
  verify_bundle "$bundle"
  for variant in "$bundle"/*; do
    [[ -d "$variant" ]] || continue
    verify_bundle "$variant"
  done
done

exit $EXIT_CODE
