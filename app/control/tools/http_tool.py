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
            return "آدرس نامعتبر است."
        if not any(host.endswith(domain) for domain in self.allow):
            return "دامنه مجاز نیست."
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text[:20_000]
        except Exception as exc:
            return f"درخواست با خطا مواجه شد: {exc}"
