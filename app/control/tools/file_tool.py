"""File system helper for the agent."""

from __future__ import annotations

import pathlib


class FileReadTool:
    """Read UTF-8 text files from whitelisted directories."""

    name = "file.read"

    def __init__(self, allow_dirs: list[str] | tuple[str, ...]) -> None:
        if not allow_dirs:
            raise ValueError("allow_dirs must not be empty")
        self.allow_dirs = [pathlib.Path(path).resolve() for path in allow_dirs]

    def _is_allowed(self, path: pathlib.Path) -> bool:
        return any(str(path).startswith(str(prefix)) for prefix in self.allow_dirs)

    def run(self, path: str, max_bytes: int = 20_000) -> str:
        candidate = pathlib.Path(path).expanduser().resolve()
        if not self._is_allowed(candidate):
            return "\u062f\u0633\u062a\u0631\u0633\u06cc \u0645\u062c\u0627\u0632 \u0646\u06cc\u0633\u062a."
        if not candidate.exists() or candidate.is_dir():
            return "\u067e\u0631\u0648\u0646\u062f\u0647 \u06cc\u0627\u0641\u062a \u0646\u0634\u062f."
        data = candidate.read_bytes()[:max_bytes]
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return "[binary]"
