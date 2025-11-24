import pytest

from os.control.os.config import Settings


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, ["*"]),
        ("", ["*"]),
        ("*", ["*"]),
        ("http://localhost:3001", ["http://localhost:3001"]),
        (
            "http://localhost:3000,http://localhost:3001",
            ["http://localhost:3000", "http://localhost:3001"],
        ),
        (
            '["http://localhost:3000","http://localhost:3001"]',
            ["http://localhost:3000", "http://localhost:3001"],
        ),
    ],
)
def test_cors_origins_parsing(monkeypatch: pytest.MonkeyPatch, value: str | None, expected):
    monkeypatch.delenv("AION_CONTROL_CORS_ORIGINS", raising=False)
    if value is not None:
        monkeypatch.setenv("AION_CONTROL_CORS_ORIGINS", value)

    settings = Settings()

    assert settings.cors_origins == expected


def test_cors_origins_invalid(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AION_CONTROL_CORS_ORIGINS", "[invalid]")

    with pytest.raises(ValueError):
        Settings()
