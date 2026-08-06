from __future__ import annotations

import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SKILLS = {
    "code-review",
    "database",
    "deployment",
    "refactor",
    "reporting",
    "security",
    "ui-ux",
}


def test_root_agents_contract_is_action_first() -> None:
    instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert re.search(r"The impact\s+analysis is not a stopping gate", instructions)
    assert "Do not replace implementation" in instructions
    assert "Markdown is supporting work, not the primary deliverable" in instructions
    assert "Stay on the currently checked-out branch" in instructions


def test_project_codex_config_is_safe_and_reviewable() -> None:
    config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))

    assert config["model_reasoning_effort"] in {"medium", "high", "xhigh"}
    assert config["model_verbosity"] == "low"
    assert config["approval_policy"] == "on-request"
    assert config["sandbox_mode"] == "workspace-write"
    assert "model" not in config
    assert "model_provider" not in config


def test_repository_skills_use_the_supported_discovery_path() -> None:
    skill_root = ROOT / ".agents" / "skills"
    skill_files = sorted(skill_root.glob("*/SKILL.md"))
    discovered_names: set[str] = set()

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        assert frontmatter, f"missing YAML frontmatter: {skill_file}"

        name = re.search(r"^name:\s*(\S+)\s*$", frontmatter.group(1), re.MULTILINE)
        description = re.search(
            r"^description:\s*(\S.*)\s*$", frontmatter.group(1), re.MULTILINE
        )
        assert name, f"missing skill name: {skill_file}"
        assert description, f"missing skill description: {skill_file}"
        discovered_names.add(name.group(1))

    assert discovered_names == EXPECTED_SKILLS


def test_codex_wrappers_do_not_hide_or_skip_failures() -> None:
    test_ps1 = (ROOT / ".codex" / "scripts" / "test.ps1").read_text(encoding="utf-8-sig")
    test_sh = (ROOT / ".codex" / "scripts" / "test.sh").read_text(encoding="utf-8-sig")
    lint_ps1 = (ROOT / ".codex" / "scripts" / "lint.ps1").read_text(encoding="utf-8-sig")
    lint_sh = (ROOT / ".codex" / "scripts" / "lint.sh").read_text(encoding="utf-8-sig")

    assert "pytest.ini" not in test_ps1
    assert "pytest.ini" not in test_sh
    assert "tests/architecture" in test_ps1
    assert "tests/architecture" in test_sh
    assert "not test_structure_migration_gate" in test_ps1
    assert "not test_structure_migration_gate" in test_sh
    assert "exit 1" in test_ps1
    assert "exit 1" in test_sh
    assert "exit 1" in lint_ps1
    assert "exit 1" in lint_sh
    assert "|| true" not in lint_sh
