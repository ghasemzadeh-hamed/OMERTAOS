from __future__ import annotations

from importlib import import_module

import pytest

from control.clients.models import LLMProviderDisabled, call_llm
from integrations.providers import LLMProviderError, call_openai_compatible


class FakeResponse:
    def __init__(self, status_code: int = 200, payload: object | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {"choices": [{"message": {"content": "ok"}}]}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> object:
        return self._payload


def test_http_provider_uses_bounded_request_without_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_post(endpoint: str, **kwargs: object) -> FakeResponse:
        captured.update({"endpoint": endpoint, **kwargs})
        return FakeResponse()

    monkeypatch.setattr("integrations.providers.http_llm.requests.post", fake_post)

    result = call_openai_compatible(
        "https://provider.example/v1/chat",
        "secret-value",
        "model-1",
        "system",
        [{"role": "user", "content": "hello"}],
        100,
        0.2,
        2500,
    )

    assert result == "ok"
    assert captured["timeout"] == 2.5
    assert captured["allow_redirects"] is False
    assert captured["headers"] == {
        "Content-Type": "application/json",
        "Authorization": "Bearer secret-value",
    }


def test_http_provider_rejects_redirect_and_invalid_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "integrations.providers.http_llm.requests.post",
        lambda *args, **kwargs: FakeResponse(status_code=302),
    )
    with pytest.raises(LLMProviderError, match="redirects"):
        call_openai_compatible("https://provider.example", None, "m", "", [], 10, 0, 1000)

    monkeypatch.setattr(
        "integrations.providers.http_llm.requests.post",
        lambda *args, **kwargs: FakeResponse(payload={"choices": []}),
    )
    with pytest.raises(LLMProviderError, match="invalid response shape"):
        call_openai_compatible("https://provider.example", None, "m", "", [], 10, 0, 1000)


def test_local_provider_does_not_forward_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_call(*args: object) -> str:
        captured["args"] = args
        return "local-ok"

    monkeypatch.setattr("control.clients.models.client.call_openai_compatible", fake_call)

    result = call_llm(
        {"provider": "local", "endpoint": "http://localhost:11434", "api_key": "must-not-send"},
        "",
        [],
        10,
        0,
    )

    assert result == "local-ok"
    assert captured["args"][1] is None


def test_disabled_unknown_and_invalid_endpoint_fail_closed() -> None:
    with pytest.raises(LLMProviderDisabled, match="disabled"):
        call_llm({"provider": "disabled"}, "", [], 10, 0)
    with pytest.raises(LLMProviderDisabled, match="Unknown provider"):
        call_llm({"provider": "other"}, "", [], 10, 0)
    with pytest.raises(LLMProviderError, match="absolute HTTP"):
        call_openai_compatible("file:///tmp/model", None, "m", "", [], 10, 0, 1000)


def test_legacy_model_client_is_retired() -> None:
    with pytest.raises(ModuleNotFoundError):
        import_module("models.client")
