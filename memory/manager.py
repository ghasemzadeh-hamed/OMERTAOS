"""Coordinates vector, object, and relational stores for workflow memory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class MemoryProfile:
    def __init__(self, name: str, chunk_size: int, overlap: int, embed_model: str) -> None:
        self.name = name
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embed_model = embed_model

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "chunk_size": self.chunk_size,
            "overlap": self.overlap,
            "embed_model": self.embed_model,
        }


class MemoryManager:
    """Tracks dataset ingests and metadata for workflow recall."""

    def __init__(self, catalog_path: Path | None = None) -> None:
        self.catalog_path = catalog_path or Path("/tmp/aion_memory_catalog.json")
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.profiles: Dict[str, MemoryProfile] = {
            "shortform": MemoryProfile("shortform", 512, 32, "text-embedding-3-small"),
            "longform": MemoryProfile("longform", 1024, 64, "text-embedding-3-large"),
            "code": MemoryProfile("code", 768, 40, "code-search"),
            "images": MemoryProfile("images", 256, 16, "vision-clip"),
        }
        self.datasets: List[Dict[str, object]] = []
        self._load()

    def _load(self) -> None:
        if self.catalog_path.exists():
            payload = json.loads(self.catalog_path.read_text())
            self.datasets = payload.get("datasets", [])
            for profile_payload in payload.get("profiles", []):
                profile = MemoryProfile(
                    profile_payload["name"],
                    profile_payload["chunk_size"],
                    profile_payload["overlap"],
                    profile_payload["embed_model"],
                )
                self.profiles[profile.name] = profile

    def _persist(self) -> None:
        payload = {
            "profiles": [profile.to_dict() for profile in self.profiles.values()],
            "datasets": self.datasets,
        }
        self.catalog_path.write_text(json.dumps(payload, indent=2))

    def register_profile(self, profile: MemoryProfile) -> None:
        self.profiles[profile.name] = profile
        self._persist()

    def list_profiles(self) -> List[Dict[str, object]]:
        return [profile.to_dict() for profile in self.profiles.values()]

    def ingest(self, dataset: Dict[str, object]) -> Dict[str, object]:
        dataset["status"] = "INGESTED"
        self.datasets.append(dataset)
        self._persist()
        return dataset

    def list_datasets(self) -> List[Dict[str, object]]:
        return list(self.datasets)

    def find_dataset(self, dataset_id: str) -> Optional[Dict[str, object]]:
        for dataset in self.datasets:
            if dataset.get("dataset_id") == dataset_id:
                return dataset
        return None
