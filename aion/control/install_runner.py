from __future__ import annotations

import os
import pathlib
import shlex
import subprocess
from typing import Dict, Optional


ENV_ROOT = pathlib.Path(os.getenv("AION_ENV_ROOT", "/opt/aion/envs"))
VENDOR_ROOT = pathlib.Path(os.getenv("AION_VENDOR_ROOT", "/opt/aion/vendor"))


def ensure_venv(env: str) -> pathlib.Path:
    root = ENV_ROOT / env
    py = root / "bin" / "python"
    if not py.exists():
        root.mkdir(parents=True, exist_ok=True)
        subprocess.run(["python", "-m", "venv", str(root)], check=True)
        subprocess.run([str(py), "-m", "pip", "install", "-U", "pip", "setuptools", "wheel"], check=True)
    return py


def build_install_cmd(
    name: str,
    version: Optional[str],
    editable: bool,
    repo_url: Optional[str],
    py: pathlib.Path,
) -> list[str]:
    if editable:
        if not repo_url:
            raise ValueError("Editable installations require a repository URL")
        vendor = VENDOR_ROOT / name
        vendor.parent.mkdir(parents=True, exist_ok=True)
        clone_cmd = f"git clone {shlex.quote(repo_url)} {shlex.quote(str(vendor))} || true"
        install_cmd = f"{shlex.quote(str(py))} -m pip install -e {shlex.quote(str(vendor))}"
        return ["bash", "-lc", f"{clone_cmd} && {install_cmd}"]

    version_suffix = f"=={version}" if version else ""
    return [str(py), "-m", "pip", "install", f"{name}{version_suffix}"]


def install(
    name: str,
    env: str = "default",
    version: Optional[str] = None,
    editable: bool = False,
    repo_url: Optional[str] = None,
) -> Dict[str, str]:
    py = ensure_venv(env)
    cmd = build_install_cmd(name, version, editable, repo_url, py)
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        status = "installed"
    except subprocess.CalledProcessError as exc:  # pragma: no cover - defensive
        output = exc.output
        status = "failed"
    return {"status": status, "log": output}
