"""Train router policy model using historical features."""
import json
from pathlib import Path

features_path = Path("/tmp/router_features.json")
if not features_path.exists():
    raise SystemExit("Missing feature file")

features = json.loads(features_path.read_text())
model = {"intents": list(features.keys()), "version": "1.0.0"}
Path("/tmp/router_model.json").write_text(json.dumps(model))
print("Trained router model")
