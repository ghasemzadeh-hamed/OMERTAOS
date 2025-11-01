"""Install a model defined in the Agent-OS AI Registry."""
from __future__ import annotations

import argparse
import hashlib
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Iterable
import urllib.request
import zipfile

import yaml

REGISTRY_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_INDEX = REGISTRY_ROOT / "REGISTRY.yaml"
DEFAULT_INSTALL_ROOT = Path("/opt/ai-models")


class InstallError(RuntimeError):
    """Raised when an installation step fails."""


def _load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _require_admin(approved: bool) -> None:
    if not approved:
        raise InstallError("Admin approval required. Re-run with --approve to continue.")


def _download(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response, destination.open("wb") as fh:
        shutil.copyfileobj(response, fh)


def _verify_sha256(file_path: Path, expected: str) -> bool:
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return digest.lower() == expected.lower()


def _extract(archive: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    if tarfile.is_tarfile(archive):
        with tarfile.open(archive, "r:*") as tar:
            tar.extractall(target_dir)
    elif zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive, "r") as zip_ref:
            zip_ref.extractall(target_dir)
    else:
        # Fallback: copy as-is
        shutil.copy2(archive, target_dir / archive.name)


def _update_registry(name: str, install_path: Path) -> None:
    registry = _load_yaml(REGISTRY_INDEX)
    registry.setdefault("installed", {}).setdefault("models", {})[name] = str(install_path)
    with REGISTRY_INDEX.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(registry, fh, sort_keys=False)


def install(model_name: str, approve: bool, manifest_root: Path, install_root: Path) -> Path:
    _require_admin(approve)

    manifest_path = manifest_root / f"models/{model_name}.yaml"
    if not manifest_path.exists():
        # support nested provider directories (e.g., models/provider/name.yaml)
        matches = list((manifest_root / "models").rglob(f"{model_name}.yaml"))
        if not matches:
            raise InstallError(f"Unknown model '{model_name}'.")
        manifest_path = matches[0]

    manifest = _load_yaml(manifest_path)
    download_info = manifest.get("download") or {}
    url = download_info.get("url")
    if not url:
        raise InstallError(f"Manifest for {model_name} does not define a download URL.")

    expected_sha = (manifest.get("integrity") or {}).get("sha256")

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / f"{model_name}.pkg"
        print(f"Downloading {model_name} from {url} ...")
        _download(url, archive_path)

        if expected_sha:
            print("Verifying SHA-256 checksum ...")
            if not _verify_sha256(archive_path, expected_sha):
                raise InstallError("Integrity check failed (SHA-256 mismatch).")
            print("Integrity verified.")
        else:
            print("Warning: no integrity information in manifest. Skipping verification.")

        target_dir = install_root / model_name
        print(f"Installing into {target_dir} ...")
        _extract(archive_path, target_dir)

    _update_registry(model_name, target_dir)
    print(f"{model_name} installed successfully!")
    return target_dir


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Model identifier to install")
    parser.add_argument("--approve", action="store_true", help="Confirm admin approval")
    parser.add_argument(
        "--manifest-root",
        type=Path,
        default=REGISTRY_ROOT,
        help="Path to the registry root (default: registry directory)",
    )
    parser.add_argument(
        "--install-root",
        type=Path,
        default=DEFAULT_INSTALL_ROOT,
        help="Installation root directory",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        install(args.model, args.approve, args.manifest_root, args.install_root)
    except InstallError as exc:
        print(f"ERROR: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - guardrail for unexpected errors
        print(f"ERROR: Unexpected error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
