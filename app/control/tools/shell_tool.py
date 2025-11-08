"""Restricted shell execution for the agent."""

from __future__ import annotations

import shlex
import subprocess


class ShellTool:
    """Execute allow-listed shell commands."""

    name = "ops.shell"

    def __init__(self, allow: list[str] | tuple[str, ...]) -> None:
        if not allow:
            raise ValueError("allow list must not be empty")
        self.allow = {cmd.strip(): None for cmd in allow}

    def run(self, cmd: str) -> str:
        if not cmd.strip():
            return "دستور نامعتبر است."
        head = shlex.split(cmd)[0]
        if head not in self.allow:
            return f"اجازه اجرای '{head}' وجود ندارد."
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except subprocess.TimeoutExpired:
            return "اجرای فرمان زمان‌بر شد و متوقف گردید."
        output = result.stdout or result.stderr
        return (output or "بدون خروجی.")[:10_000]
