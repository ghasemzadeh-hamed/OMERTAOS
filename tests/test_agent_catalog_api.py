from pathlib import Path

from fastapi.testclient import TestClient

from os.control.os.agent_catalog import AgentCatalog
from os.control.os.http import app


def test_agent_catalog_loader_reads_templates_and_recipes():
    catalog = AgentCatalog(root=Path("config/agent_catalog"))
    templates = catalog.list_templates()
    ids = {template.id for template in templates}
    assert {"crewai-crm", "autogpt-research", "superagi-github"}.issubset(ids)

    template = catalog.get_template("autogpt-research")
    assert template is not None
    recipe = catalog.load_recipe(template.recipe)
    assert recipe.get("agent", {}).get("id") == "autogpt-research"


def test_agent_catalog_api_supports_create_and_deploy():
    headers = {"x-aion-roles": "ROLE_ADMIN"}
    with TestClient(app) as client:
        catalog_response = client.get("/api/agent-catalog", headers=headers)
        assert catalog_response.status_code == 200
        payload = catalog_response.json()
        assert payload["agents"], "catalog should expose templates"

        create_payload = {
            "template_id": "autogpt-research",
            "name": "Research Copilot",
            "config": {"search_provider": "tavily", "llm_profile": "openai", "max_budget": 5},
            "scope": "tenant",
            "enabled": True,
        }
        create_response = client.post("/api/agents", json=create_payload, headers=headers)
        assert create_response.status_code == 201
        agent = create_response.json()
        assert agent["template_id"] == "autogpt-research"

        deploy_response = client.post(f"/api/agents/{agent['id']}/deploy", headers=headers)
        assert deploy_response.status_code == 200
        deployed = deploy_response.json()
        assert deployed["status"] == "active"
