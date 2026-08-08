from __future__ import annotations

from .models import ProxyProfile

CONTAINER_PROXY_LISTEN = "0.0.0.0"  # nosec B104 - sibling containers require this listener


def build_xray_outbound(profile: ProxyProfile, secrets: dict[str, str] | None = None) -> dict[str, object]:
    if profile.type == "direct":
        return {"tag": "direct", "protocol": "freedom"}
    if profile.type == "http":
        return {
            "tag": f"proxy-{profile.id}",
            "protocol": "http",
            "settings": {"servers": [{"address": profile.host, "port": profile.port}]},
        }
    if profile.type == "socks5":
        return {
            "tag": f"proxy-{profile.id}",
            "protocol": "socks",
            "settings": {"servers": [{"address": profile.host, "port": profile.port}]},
        }
    if profile.type == "vless":
        return {
            "tag": f"proxy-{profile.id}",
            "protocol": "vless",
            "settings": {
                "vnext": [
                    {
                        "address": profile.host,
                        "port": profile.port,
                        "users": [
                            {
                                "id": (secrets or {}).get("uuid", ""),
                                "encryption": "none",
                                "flow": profile.flow or "",
                            }
                        ],
                    }
                ]
            },
            "streamSettings": {
                "network": profile.transport or "tcp",
                "security": profile.security or "none",
                "tlsSettings": {"serverName": profile.sni} if profile.sni else {},
                "wsSettings": {"path": profile.path} if profile.path else {},
            },
        }
    raise ValueError(f"Unsupported proxy type: {profile.type}")


def build_xray_config(profile: ProxyProfile, secrets: dict[str, str] | None = None) -> dict[str, object]:
    outbound = build_xray_outbound(profile, secrets)
    outbounds = [outbound]
    if profile.fallback_direct:
        outbounds.append({"tag": "direct", "protocol": "freedom"})
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "tag": "socks-in",
                "listen": CONTAINER_PROXY_LISTEN,
                "port": 10808,
                "protocol": "socks",
                "settings": {"udp": True},
            },
            {
                "tag": "http-in",
                "listen": CONTAINER_PROXY_LISTEN,
                "port": 10809,
                "protocol": "http",
            },
        ],
        "outbounds": outbounds,
    }
