#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.."; pwd)"
PROFILE="${PROFILE:-user}"

cp -n "$ROOT/shared/gateway/.env.example" "$ROOT/shared/gateway/.env" 2>/dev/null || true
cp -n "$ROOT/shared/control/.env.example" "$ROOT/shared/control/.env" 2>/dev/null || true

if [[ "$PROFILE" == "ent" ]]; then
  sed -i.bak 's/FEATURE_SEAL=0/FEATURE_SEAL=1/' "$ROOT/shared/gateway/.env" || true
else
  sed -i.bak 's/FEATURE_SEAL=1/FEATURE_SEAL=0/' "$ROOT/shared/gateway/.env" || true
fi
rm -f "$ROOT/shared/gateway/.env.bak"

python - "$ROOT" "$PROFILE" <<'PY'
import sys
from pathlib import Path
root = Path(sys.argv[1])
profile = sys.argv[2]
path = root / "shared" / "control" / ".env"
if path.exists():
    lines = path.read_text().splitlines()
else:
    lines = []
found = False
for idx, line in enumerate(lines):
    if line.startswith("PROFILE="):
        lines[idx] = f"PROFILE={profile}"
        found = True
        break
if not found:
    lines.append(f"PROFILE={profile}")
path.write_text("\n".join(lines) + "\n")
PY

export PROFILE

(
  cd "$ROOT/shared/control" && \
  source "$ROOT/.venv/bin/activate" && \
  uvicorn core.chatops:app --factory --port 8010 --reload
) & CTRL_PID=$!

(
  cd "$ROOT/shared/gateway" && \
  node --loader ts-node/esm src/server.ts
) & GW_PID=$!

echo "Gateway: http://127.0.0.1:8000  Control: http://127.0.0.1:8010  PROFILE=$PROFILE"
wait $CTRL_PID $GW_PID
