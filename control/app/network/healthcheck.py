from __future__ import annotations

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
    proxy_url = proxy_url_for(profile)
    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
        return {
            "ok": response.status_code < 500,
            "status_code": response.status_code,
            "target_url": url,
            "routed_via": profile.type,
        }
    except Exception as exc:
        if profile.fallback_direct and profile.type != "direct":
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    response = await client.get(url)
                return {
                    "ok": response.status_code < 500,
                    "status_code": response.status_code,
                    "target_url": url,
                    "routed_via": "direct_fallback",
                }
            except Exception as fallback_exc:
                exc = fallback_exc
        return {
            "ok": False,
            "status_code": None,
            "target_url": url,
            "routed_via": profile.type,
            "error": str(exc),
        }

