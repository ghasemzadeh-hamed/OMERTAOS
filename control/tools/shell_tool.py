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
            return "\u062f\u0633\u062a\u0648\u0631 \u0646\u0627\u0645\u0639\u062a\u0628\u0631 \u0627\u0633\u062a."
        head = shlex.split(cmd)[0]
        if head not in self.allow:
            return f"\u0627\u062c\u0627\u0632\u0647 \u0627\u062c\u0631\u0627\u06cc '{head}' \u0648\u062c\u0648\u062f \u0646\u062f\u0627\u0631\u062f."
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
            return "\u0627\u062c\u0631\u0627\u06cc \u0641\u0631\u0645\u0627\u0646 \u0632\u0645\u0627\u0646\u200c\u0628\u0631 \u0634\u062f \u0648 \u0645\u062a\u0648\u0642\u0641 \u06af\u0631\u062f\u06cc\u062f."
        output = result.stdout or result.stderr
        return (output or "\u0628\u062f\u0648\u0646 \u062e\u0631\u0648\u062c\u06cc.")[:10_000]
