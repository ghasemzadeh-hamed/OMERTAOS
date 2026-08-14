from pathlib import Path

from os.kernel.policy_engine import PolicyEngine


def test_policy_denies_role(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.json"
    policy_file.write_text(
        '{"intent":{"default":true,"deny_roles":["blocked"],"tags":["test"],"max_risk":0.5}}',
        encoding="utf-8",
    )
    engine = PolicyEngine(policy_path=policy_file)
    result = engine.evaluate("intent", {"roles": ["blocked"], "risk_score": 0.2})
    assert not result.allowed
    assert result.reason == "role_denied"
    assert result.requires_supervision


def test_policy_allows_within_limits(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.json"
    policy_file.write_text('{"intent":{"default":true,"rate_limit_per_minute":2}}', encoding="utf-8")
    engine = PolicyEngine(policy_path=policy_file)
    first = engine.evaluate("intent", {"roles": []})
    second = engine.evaluate("intent", {"roles": []})
    assert first.allowed and second.allowed
    third = engine.evaluate("intent", {"roles": []})
    assert not third.allowed
    assert third.reason == "rate_limited"
