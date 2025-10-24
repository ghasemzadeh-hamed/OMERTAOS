"""Transform router decision rows into feature aggregates."""
import json
from pathlib import Path

input_path = Path("/tmp/router_decisions.json")
output_path = Path("/tmp/router_features.json")

if input_path.exists():
    rows = json.loads(input_path.read_text())
else:
    rows = []

features = {}
for row in rows:
    intent = row.get("intent")
    features.setdefault(intent, {"count": 0})
    features[intent]["count"] += 1

output_path.write_text(json.dumps(features))
print(f"Generated features for {len(features)} intents")
