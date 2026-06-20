from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProxyType(str, Enum):
    direct = "direct"
    http = "http"
    socks5 = "socks5"
    vless = "vless"


class ProxyScope(str, Enum):
    global_ = "global"
    ai_providers = "ai_providers"
    model_registry = "model_registry"
    agent_runtime = "agent_runtime"
    custom_domains = "custom_domains"


class ProxySecrets(BaseModel):
    uuid: str | None = None
    password: str | None = None
    private_key: str | None = None
    public_key: str | None = None
    short_id: str | None = None


class ProxyProfileBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(min_length=1, max_length=120)
    type: ProxyType
    enabled: bool = False
    scope: ProxyScope = ProxyScope.global_
    host: str | None = Field(default=None, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    transport: str | None = Field(default=None, max_length=48)
    security: str | None = Field(default=None, max_length=48)
    sni: str | None = Field(default=None, max_length=255)
    flow: str | None = Field(default=None, max_length=80)
    path: str | None = Field(default=None, max_length=255)
    fallback_direct: bool = False
    health_check_url: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def validate_endpoint(self) -> "ProxyProfileBase":
        if self.type != ProxyType.direct and (not self.host or not self.port):
            raise ValueError("host and port are required for proxy profiles")
        return self


class ProxyProfileCreate(ProxyProfileBase):
    secrets: ProxySecrets | None = None


class ProxyProfileUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str | None = Field(default=None, min_length=1, max_length=120)
    type: ProxyType | None = None
    enabled: bool | None = None
    scope: ProxyScope | None = None
    host: str | None = Field(default=None, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    transport: str | None = Field(default=None, max_length=48)
    security: str | None = Field(default=None, max_length=48)
    sni: str | None = Field(default=None, max_length=255)
    flow: str | None = Field(default=None, max_length=80)
    path: str | None = Field(default=None, max_length=255)
    fallback_direct: bool | None = None
    health_check_url: str | None = Field(default=None, max_length=512)
    secrets: ProxySecrets | None = None


class ProxyProfileOut(ProxyProfileBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    is_default: bool = False
    has_secrets: bool = False
    created_at: datetime
    updated_at: datetime


class ProxyProfileList(BaseModel):
    items: list[ProxyProfileOut]


class ProxyTestResult(BaseModel):
    ok: bool
    status_code: int | None = None
    target_url: str
    routed_via: str
    error: str | None = None
