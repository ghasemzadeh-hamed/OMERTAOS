from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RouterConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: Literal["auto", "local", "api"] = "auto"
    local_provider: str | None = Field(default=None, max_length=160)
    api_provider: str | None = Field(default=None, max_length=160)


class ConfigurationProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    router: RouterConfiguration
