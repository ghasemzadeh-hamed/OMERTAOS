"""Shared utilities for interacting with the Control API from terminal UIs."""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional

import requests


class ControlAPIError(RuntimeError):
    """Raised when the Control API returns a non-successful response."""

    def __init__(self, message: str, *, response: Optional[requests.Response] = None) -> None:
        super().__init__(message)
        self.response = response


@dataclass
class ControlAPI:
    """Thin HTTP client for the OMERTAOS Control API."""

    base_url: str
    token: Optional[str] = None
    timeout: int = 15
    verify: bool = True
    _session: requests.Session = field(default_factory=requests.Session, init=False, repr=False)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if self.token:
            self._session.headers.update({"Authorization": f"Bearer {self.token}"})
        self._session.headers.setdefault("Accept", "application/json")

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        response = self._session.request(method, url, timeout=self.timeout, verify=self.verify, **kwargs)
        if response.status_code >= 400:
            detail = self._format_error(response)
            raise ControlAPIError(detail, response=response)
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.text

    def _format_error(self, response: requests.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            payload = {"detail": response.text or response.reason}
        detail = payload.get("detail") if isinstance(payload, Mapping) else None
        if detail and isinstance(detail, (str, list)):
            return f"{response.status_code}: {detail}"
        return f"{response.status_code}: {response.text or response.reason}"

    # Provider operations -------------------------------------------------

    def list_providers(self) -> List[Dict[str, Any]]:
        payload = self._request("GET", "/api/providers")
        if isinstance(payload, Mapping) and "items" in payload:
            return list(payload["items"])
        if isinstance(payload, list):
            return payload
        return []

    def create_provider(self, definition: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._request("POST", "/api/providers", json=definition)

    # Router operations ---------------------------------------------------

    def set_router_policy(self, policy: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._request("POST", "/api/router/policy", json=policy)

    def reload_router_policy(self) -> Mapping[str, Any]:
        return self._request("POST", "/api/router/policy/reload", json={})

    # Data sources --------------------------------------------------------

    def list_data_sources(self) -> List[Dict[str, Any]]:
        payload = self._request("GET", "/api/data-sources")
        if isinstance(payload, Mapping) and "items" in payload:
            return list(payload["items"])
        if isinstance(payload, list):
            return payload
        return []

    def create_data_source(self, definition: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._request("POST", "/api/data-sources", json=definition)

    def test_data_source(self, name: str) -> Mapping[str, Any]:
        return self._request("POST", f"/api/data-sources/{name}/test", json={})

    # Modules -------------------------------------------------------------

    def list_modules(self) -> List[Dict[str, Any]]:
        payload = self._request("GET", "/api/modules")
        if isinstance(payload, Mapping) and "items" in payload:
            return list(payload["items"])
        if isinstance(payload, list):
            return payload
        return []

    def deploy_module(self, definition: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._request("POST", "/api/modules", json=definition)


HELP_TEXT = """فرمان‌های پشتیبانی‌شده:
  help                               نمایش این راهنما
  list providers|modules|datasources لیست منابع از کنترل
  add provider <name> key=... [kind=local|api] [base_url=...]
  add ds <name> kind=postgres dsn=postgres://... [readonly=true]
  set router policy=<default|auto> [budget=200] [failover=on|off]
  reload router                      بارگذاری مجدد سیاست مسیردهی
  test ds <name>                     اجرای تست اتصال دیتاسورس
"""


class CommandProcessor:
    """Parses simple chat-style commands and maps them to Control API calls."""

    def __init__(self, api: ControlAPI) -> None:
        self.api = api

    def execute(self, command: str) -> str:
        command = command.strip()
        if not command:
            return ""
        try:
            parts = shlex.split(command)
        except ValueError as exc:  # unmatched quotes etc.
            return f"❌ خطا در خواندن فرمان: {exc}"
        if not parts:
            return ""
        action = parts[0].lower()
        try:
            if action == "help":
                return HELP_TEXT
            if action == "list" and len(parts) > 1:
                return self._handle_list(parts[1])
            if action == "add" and len(parts) > 2:
                target = parts[1].lower()
                if target in {"provider", "providers"}:
                    return self._handle_add_provider(parts[2:])
                if target in {"ds", "datasource", "datasources"}:
                    return self._handle_add_datasource(parts[2:])
            if action == "set" and len(parts) > 1 and parts[1].lower() == "router":
                return self._handle_set_router(parts[2:])
            if action == "reload" and len(parts) > 1 and parts[1].lower() == "router":
                self.api.reload_router_policy()
                return "🔄 سیاست مسیردهی مجدداً بارگذاری شد."
            if action == "test" and len(parts) > 2 and parts[1].lower() in {"ds", "datasource"}:
                name = parts[2]
                result = self.api.test_data_source(name)
                return f"🧪 نتیجهٔ تست دیتاسورس {name}: {json.dumps(result, ensure_ascii=False)}"
            return f"⚠️ فرمان ناشناخته. `help` را برای فهرست دستورها وارد کنید."
        except ControlAPIError as exc:
            detail = self._format_error(exc)
            return f"❌ خطا از API: {detail}"

    def _handle_list(self, what: str) -> str:
        what = what.lower()
        if what in {"providers", "provider"}:
            providers = self.api.list_providers()
            if not providers:
                return "ℹ️ هیچ Provider فعالی یافت نشد."
            lines = ["📡 Providers:"]
            for provider in providers:
                lines.append(self._format_summary(provider, ["name", "kind", "status"]))
            return "\n".join(lines)
        if what in {"modules", "module"}:
            modules = self.api.list_modules()
            if not modules:
                return "ℹ️ ماژولی ثبت نشده است."
            lines = ["🧩 Modules:"]
            for module in modules:
                lines.append(self._format_summary(module, ["name", "version", "status"]))
            return "\n".join(lines)
        if what in {"datasources", "datasource", "ds"}:
            data_sources = self.api.list_data_sources()
            if not data_sources:
                return "ℹ️ هیچ Data Source فعالی وجود ندارد."
            lines = ["🗄️ Data Sources:"]
            for ds in data_sources:
                lines.append(self._format_summary(ds, ["name", "kind", "status"]))
            return "\n".join(lines)
        return "⚠️ نوع لیست پشتیبانی نمی‌شود."

    def _handle_add_provider(self, args: Iterable[str]) -> str:
        args = list(args)
        params = self._consume_params(args)
        name = params.pop("name", args[0] if args else None)
        if not name:
            return "⚠️ نام Provider مشخص نشده است (name=...)."
        definition: Dict[str, Any] = {
            "name": name,
            "kind": params.pop("kind", "api" if "api_key" in params else "local"),
        }
        base_url = params.pop("base_url", None)
        if base_url:
            definition["base_url"] = base_url
        config: Dict[str, Any] = {}
        api_key = params.pop("key", params.pop("api_key", None))
        if api_key:
            config["api_key"] = api_key
        if params:
            config.update(params)
        if config:
            definition["config"] = config
        created = self.api.create_provider(definition)
        return f"✅ Provider `{name}` ثبت شد: {json.dumps(created, ensure_ascii=False)}"

    def _handle_add_datasource(self, args: Iterable[str]) -> str:
        args = list(args)
        params = self._consume_params(args)
        name = params.pop("name", args[0] if args else None)
        if not name:
            return "⚠️ نام دیتاسورس مشخص نشده است (name=...)."
        kind = params.pop("kind", None)
        if not kind:
            return "⚠️ نوع دیتاسورس (kind=...) اجباری است."
        definition: Dict[str, Any] = {"name": name, "kind": kind, "config": params}
        created = self.api.create_data_source(definition)
        return f"✅ دیتاسورس `{name}` اضافه شد: {json.dumps(created, ensure_ascii=False)}"

    def _handle_set_router(self, args: Iterable[str]) -> str:
        args = list(args)
        params = self._consume_params(args)
        policy = params.get("policy", params.get("mode", "auto"))
        payload: Dict[str, Any] = {"default_policy": policy}
        budget = params.get("budget")
        if budget is not None:
            payload.setdefault("budgets", {})["monthly_usd"] = float(budget)
        failover = params.get("failover")
        if isinstance(failover, str):
            payload.setdefault("budgets", {})["failover"] = failover.lower() in {"on", "true", "1", "yes"}
        response = self.api.set_router_policy(payload)
        return f"✅ سیاست مسیردهی به‌روزرسانی شد: {json.dumps(response, ensure_ascii=False)}"

    def _format_error(self, exc: ControlAPIError) -> str:
        if exc.response is None:
            return str(exc)
        return exc.args[0]

    def _format_summary(self, item: Mapping[str, Any], keys: Iterable[str]) -> str:
        parts = []
        for key in keys:
            if key in item and item[key] is not None:
                parts.append(f"{key}={item[key]}")
        if not parts:
            return json.dumps(item, ensure_ascii=False)
        return " • ".join(parts)

    def _consume_params(self, args: Iterable[str]) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        for token in args:
            if "=" in token:
                key, value = token.split("=", 1)
                params[key.strip().lower()] = value.strip()
        return params

