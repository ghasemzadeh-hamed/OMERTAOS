"""Simple HTTP GET tool with domain allow list."""

from __future__ import annotations

from urllib.parse import urlparse

import requests


class HttpGetTool:
    """Perform HTTP GET requests against approved domains."""

    name = "http.get"

    def __init__(self, allow_domains: list[str] | tuple[str, ...]) -> None:
        if not allow_domains:
            raise ValueError("allow_domains must not be empty")
        self.allow = {domain.lower(): None for domain in allow_domains}

    def run(self, url: str, timeout: int = 10) -> str:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if not host:
            return "\u0622\u062f\u0631\u0633 \u0646\u0627\u0645\u0639\u062a\u0628\u0631 \u0627\u0633\u062a."
        if not any(host.endswith(domain) for domain in self.allow):
            return "\u062f\u0627\u0645\u0646\u0647 \u0645\u062c\u0627\u0632 \u0646\u06cc\u0633\u062a."
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text[:20_000]
        except Exception as exc:
            return f"\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0628\u0627 \u062e\u0637\u0627 \u0645\u0648\u0627\u062c\u0647 \u0634\u062f: {exc}"
