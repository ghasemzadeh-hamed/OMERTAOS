"""Feature catalog API for platform and UI planning."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter


router = APIRouter(prefix="/api/feature-catalog", tags=["feature-catalog"])


FEATURE_CATALOG: list[dict[str, Any]] = [
    {
        "id": "core-bootstrap",
        "title": "Core / Bootstrap",
        "items": [
            "Setup & Onboarding",
            "Authentication & Sessions",
            "Authorization & RBAC",
            "Tenant & Account bootstrap",
        ],
    },
    {
        "id": "control-plane",
        "title": "Control Plane / Platform Management",
        "items": [
            "Configuration lifecycle",
            "Feature flags & experimentation",
            "Policies",
            "Registry & Catalog",
            "Governance & Audit",
        ],
    },
    {
        "id": "agents-orchestration",
        "title": "Agents Orchestration / Runtime",
        "items": [
            "Agent Catalog & Templates",
            "Agent Lifecycle",
            "Runtime Management",
            "Observability per agent",
            "Agent Debugging & Tools",
        ],
    },
    {
        "id": "models-ai-services",
        "title": "Models & AI Services",
        "items": [
            "Model Registry & Versions",
            "Model Serving & Runtime",
            "Model Governance",
            "Experimentation & Evaluation",
        ],
    },
    {
        "id": "data-management",
        "title": "Data Management & Pipelines",
        "items": [
            "Storage & Object Stores",
            "Databases & Indexes",
            "Ingest & ETL",
            "Data Versioning & Lineage",
            "Privacy & PII handling",
        ],
    },
    {
        "id": "observability",
        "title": "Observability & Monitoring",
        "items": [
            "Health & Status",
            "Logging",
            "Metrics & Dashboards",
            "Tracing",
            "Alerts & Incidents",
        ],
    },
    {
        "id": "security",
        "title": "Security & Secrets",
        "items": [
            "Secrets Management",
            "Network Security",
            "Identity Federation",
            "Compliance & Compliance Reports",
        ],
    },
    {
        "id": "infrastructure",
        "title": "Infrastructure & Deployment",
        "items": [
            "Deployment Options",
            "CI/CD Integrations",
            "Resource Management",
            "Backup & Disaster Recovery",
        ],
    },
    {
        "id": "networking-api",
        "title": "Networking & API Management",
        "items": [
            "Gateway & API Proxy",
            "API Keys & Usage",
            "Webhooks & Callbacks",
            "Edge Caching & CDN integration",
        ],
    },
    {
        "id": "dx-tools",
        "title": "Developer Experience (DX) & Tools",
        "items": [
            "API Explorer / Swagger",
            "SDKs (TS, Python, Go)",
            "CLI (omertactl)",
            "Playground / Notebook integration",
            "Schema Registry & Codegen",
            "Dev Mode (mock services, local overrides)",
        ],
    },
    {
        "id": "ui-ux",
        "title": "UI / UX Capabilities",
        "items": [
            "Schema-driven pages",
            "Dynamic navigation",
            "Component library",
            "Live logs & terminal widgets",
            "File manager / artifact browser",
            "Accessible & localized UI",
            "Theming / branding",
        ],
    },
    {
        "id": "admin-governance",
        "title": "Admin & Governance",
        "items": [
            "User & Role management",
            "Audit log viewer & export",
            "System-wide settings",
            "License & billing management",
            "Support / contact & health dashboards",
        ],
    },
    {
        "id": "business-billing",
        "title": "Business & Billing Features",
        "items": [
            "Usage tracking",
            "Cost attribution",
            "Billing cycles & invoices",
            "Quota & plan management",
        ],
    },
    {
        "id": "marketplace",
        "title": "Marketplace & Extensibility",
        "items": [
            "Plugin system",
            "Marketplace",
            "SDK for extensions",
            "Marketplace governance",
        ],
    },
    {
        "id": "testing-qa",
        "title": "Testing, QA & Reliability",
        "items": [
            "Smoke tests & health probes",
            "Integration tests harness",
            "Load & performance testing",
            "Chaos & resilience testing",
        ],
    },
    {
        "id": "data-science",
        "title": "Data Science / ML Ops",
        "items": [
            "Experiment tracking",
            "Dataset versioning & labeling",
            "Model training orchestration",
            "Metadata store",
            "Notebook & reproducibility support",
        ],
    },
    {
        "id": "automation",
        "title": "Automation & Scheduled Tasks",
        "items": [
            "Cron / scheduled workflows",
            "Automated scaling & cleanup jobs",
            "Daily/weekly reports & summaries",
        ],
    },
    {
        "id": "support-docs",
        "title": "Support & Documentation",
        "items": [
            "In-app help & guided tours",
            "Runbooks & KB articles",
            "API docs & examples",
            "Changelog & release notes",
        ],
    },
    {
        "id": "observability-extensions",
        "title": "Observability Extensions & Integrations",
        "items": [
            "Prometheus / Grafana",
            "OpenTelemetry exporters",
            "Sentry / Error reporting",
            "Third-party logging integrations",
        ],
    },
    {
        "id": "privacy-legal",
        "title": "Privacy, Legal & Ethical Controls",
        "items": [
            "Data subject requests handling",
            "Model use policies",
            "Bias & fairness checks",
            "Data retention / deletion tools",
        ],
    },
]


@router.get("")
async def get_feature_catalog() -> dict[str, Any]:
    """Return the UI feature tree used by console planning pages."""
    return {
        "total_domains": len(FEATURE_CATALOG),
        "total_feature_groups": sum(len(domain["items"]) for domain in FEATURE_CATALOG),
        "domains": FEATURE_CATALOG,
    }


__all__ = ["router", "FEATURE_CATALOG"]
