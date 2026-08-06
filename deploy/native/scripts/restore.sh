#!/usr/bin/env bash
set -euo pipefail

BACKUP=
APPLY=false
usage() {
  cat <<'EOF'
Usage: restore.sh --backup DIRECTORY [--apply] [--help]

Verify a canonical Native backup. Without --apply this is read-only. --apply
requires stopped omertaos.target and restores both PostgreSQL databases and the
Redis RDB; it never drops databases, roles, configuration, releases, or state.
EOF
}
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
while (($#)); do case "$1" in
  --backup) (($# >= 2)) || die '--backup requires a path'; BACKUP="$2"; shift ;;
  --apply) APPLY=true ;;
  --help|-h) usage; exit 0 ;;
  *) die "unknown argument: $1" ;;
esac; shift; done

[[ "$(uname -s)" == Linux ]] || die 'Native restore requires Linux'
((EUID == 0)) || die 'run as root'
[[ -d "$BACKUP" ]] || die 'backup directory is missing'
BACKUP="$(readlink -f -- "$BACKUP")"
for file in control.pgdump console.pgdump redis.rdb config.tar.gz backup.metadata backup.manifest.sha256; do
  [[ -s "$BACKUP/$file" ]] || die "backup artifact is missing: $file"
done
(cd "$BACKUP" && sha256sum --check backup.manifest.sha256)
pg_restore --list "$BACKUP/control.pgdump" >/dev/null
pg_restore --list "$BACKUP/console.pgdump" >/dev/null
[[ "$(head -c 5 "$BACKUP/redis.rdb")" == REDIS ]] || die 'Redis backup header is invalid'
tar --list --gzip --file="$BACKUP/config.tar.gz" >/dev/null
if ! "$APPLY"; then
  printf 'Native backup verification passed; no restore was applied.\n'
  exit 0
fi

systemctl is-active --quiet omertaos.target && die 'stop omertaos.target before restore'
printf 'ERROR: live restore requires an operator-reviewed database target mapping; verification passed but no destructive replacement was attempted.\n' >&2
exit 2
