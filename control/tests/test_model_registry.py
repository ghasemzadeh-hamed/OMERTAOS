from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import yaml

from os.control.models import ModelRegistry, PrivacyLevel


@pytest.fixture()
def policy_file(tmp_path: Path) -> Path:
    data = {
        "defaults": {"privacy": "local-only"},
        "models": [
            {
                "name": "local-llama",
                "provider": "ollama",
                "mode": "local",
                "engine": "chat",
                "privacy": "local-only",
                "intents": ["summarize", "general"],
                "latency_budget_ms": 1200,
            },
            {
                "name": "cloud-gpt",
                "provider": "openai",
                "mode": "api",
                "engine": "chat",
                "privacy": "allow-api",
                "intents": ["summarize"],
                "latency_budget_ms": 2200,
            },
        ],
    }
    policy = tmp_path / "models.yaml"
    policy.write_text(yaml.safe_dump(data, sort_keys=False))
    return policy


@pytest.mark.asyncio()
async def test_select_model_prefers_privacy(policy_file: Path):
    registry = ModelRegistry(policy_file=policy_file)
    record = await registry.select_model("summarize", requested_privacy=PrivacyLevel.LOCAL_ONLY, require_healthy=False)
    assert record is not None
    assert record.name == "local-llama"


@pytest.mark.asyncio()
async def test_select_model_allows_cloud_when_requested(policy_file: Path):
    registry = ModelRegistry(policy_file=policy_file)
    record = await registry.select_model("summarize", requested_privacy=PrivacyLevel.ALLOW_API, require_healthy=False)
    assert record is not None
    assert record.name == "local-llama"

    record = await registry.select_model(
        "summarize",
        requested_privacy=PrivacyLevel.ALLOW_API,
        preferred=["cloud-gpt"],
        require_healthy=False,
    )
    assert record is not None
    assert record.name == "cloud-gpt"


@pytest.mark.asyncio()
async def test_select_model_handles_missing_intent(policy_file: Path):
    registry = ModelRegistry(policy_file=policy_file)
    record = await registry.select_model("unknown", requested_privacy=PrivacyLevel.ALLOW_API, require_healthy=False)
    assert record is None


@pytest.mark.asyncio()
async def test_reload_keeps_defaults(policy_file: Path, tmp_path: Path):
    registry = ModelRegistry(policy_file=policy_file)
    assert registry.defaults["privacy"] == "local-only"

    # Modify policies and reload
    data = yaml.safe_load(policy_file.read_text())
    data["defaults"]["privacy"] = "hybrid"
    policy_file.write_text(yaml.safe_dump(data, sort_keys=False))
    registry.reload()

    assert registry.defaults["privacy"] == "hybrid"
