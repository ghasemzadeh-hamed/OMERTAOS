"""Utilities for locating the shared AION-OS configuration file.

The control plane needs to access ``aionos.config.yaml`` both when running
inside the Docker image (``/app/...``) and when developers execute the API
locally directly from the repository checkout.  Previously we hard-coded the
``/app`` path which meant local runs immediately crashed with a
``FileNotFoundError``.  The helpers in this module try a series of sensible
defaults and fall back to the repository copy when available.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List


_DEFAULT_DOCKER_PATH = Path("/app/config/aionos.config.yaml")


def _candidate_paths() -> List[Path]:
    """Return candidate config locations ordered by priority."""

    candidates: List[Path] = []

    env_path = os.getenv("AIONOS_CONFIG_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    else:
        candidates.append(_DEFAULT_DOCKER_PATH)

    cwd_candidate = Path.cwd() / "config" / "aionos.config.yaml"
    candidates.append(cwd_candidate)

    repo_candidate = Path(__file__).resolve().parents[2] / "config" / "aionos.config.yaml"
    if repo_candidate != cwd_candidate:
        candidates.append(repo_candidate)

    return candidates


def resolve_config_path(prefer_existing: bool = True) -> Path:
    """Locate the best available path for ``aionos.config.yaml``.

    The function checks, in order:

    1. ``AIONOS_CONFIG_PATH`` when it points to an existing file.
    2. The repository checkout (``./config/aionos.config.yaml``).
    3. The config shipped in the Docker image (``/app/...``).

    When ``prefer_existing`` is ``True`` (the default) the first candidate that
    already exists is returned.  Otherwise the highest-priority candidate is
    returned even if it does not exist yet.  This allows write flows such as
    the onboarding wizard to respect a custom ``AIONOS_CONFIG_PATH`` while read
    flows automatically fall back to a usable file.
    """

    candidates = _candidate_paths()
    if prefer_existing:
        for path in candidates:
            if path.is_file():
                return path

    # Either we were asked not to prefer existing files or none of the
    # candidates exist.  Fall back to the highest-priority location so callers
    # have a deterministic place to create.
    return candidates[0]


__all__ = ["resolve_config_path"]

