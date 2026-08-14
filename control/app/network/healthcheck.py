from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from .models import ProxyProfile


def proxy_url_for(profile: ProxyProfile) -> str | None:
    if profile.type == "direct":
        return None
    if profile.type == "http":
        return f"http://{profile.host}:{profile.port}"
    if profile.type == "socks5":
        return f"socks5://{profile.host}:{profile.port}"
    if profile.type == "vless":
        return "socks5://proxy-router:10808"
    return None


async def test_profile(profile: ProxyProfile, target_url: str | None = None) -> dict[str, object]:
    url = target_url or profile.health_check_url or "https://api.openai.com/v1/models"
    _validate_target_url(url)
    proxy_url = proxy_url_for(profile)
    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=10.0, follow_redirects=False) as client:
            response = await client.get(url)
        return {
            "ok": response.status_code < 500,
            "status_code": response.status_code,
            "target_url": url,
            "routed_via": profile.type,
        }
    except Exception as exc:
        error = exc
        if profile.fallback_direct and profile.type != "direct":
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                    response = await client.get(url)
                return {
                    "ok": response.status_code < 500,
                    "status_code": response.status_code,
                    "target_url": url,
                    "routed_via": "direct_fallback",
                }
            except Exception as fallback_exc:
                error = fallback_exc
        return {
            "ok": False,
            "status_code": None,
            "target_url": url,
            "routed_via": profile.type,
            "error": str(error),
        }


def _validate_target_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password or not parsed.hostname:
        raise ValueError("Health-check target must be an HTTP(S) URL without credentials")

    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(parsed.hostname, parsed.port, type=socket.SOCK_STREAM)
        }
    except (OSError, ValueError):
        raise ValueError("Health-check target host could not be resolved") from None

    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise ValueError("Health-check target must resolve only to public addresses")
