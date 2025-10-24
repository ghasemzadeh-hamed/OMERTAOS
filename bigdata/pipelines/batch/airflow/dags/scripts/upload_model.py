"""Upload trained router model to MinIO."""
from minio import Minio
from pathlib import Path

client = Minio("minio:9000", access_key="minio", secret_key="minio123", secure=False)
model_path = Path("/tmp/router_model.json")
if model_path.exists():
    client.fput_object("aion-models", "weekly/router_model.json", str(model_path))
    print("Uploaded router model")
else:
    print("Router model missing")
