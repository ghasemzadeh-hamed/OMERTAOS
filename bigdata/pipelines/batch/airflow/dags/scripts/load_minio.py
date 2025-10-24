"""Upload feature artifacts to MinIO."""
from minio import Minio
from pathlib import Path

client = Minio("minio:9000", access_key="minio", secret_key="minio123", secure=False)
features_path = Path("/tmp/router_features.json")
if features_path.exists():
    client.fput_object("aion-features", "latest/router_features.json", str(features_path))
    print("Uploaded features to MinIO")
else:
    print("No features file found")
