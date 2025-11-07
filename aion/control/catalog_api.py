from __future__ import annotations

import logging
import os
import pathlib
from typing import Any, Dict, Iterable, Optional

import yaml
from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, MetaData, String, Table, create_engine, func, or_, select
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert
from sqlalchemy.orm import Session, sessionmaker

from .install_runner import install
from .schemas import InstallReq, SaveConfigReq, UpsertPayload
from .secrets_vault import Vault


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = pathlib.Path(
    os.getenv("AION_CONFIG_FILE", BASE_DIR / "config" / "aion.yaml")
)


def _resolve_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        body = value[2:-1]
        if ":-" in body:
            var, default = body.split(":-", 1)
            return os.getenv(var, default)
        return os.getenv(body, "")
    return value


def _resolve_tree(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: _resolve_tree(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve_tree(v) for v in node]
    return _resolve_env(node)


with CONFIG_PATH.open("r", encoding="utf-8") as fh:
    CFG = _resolve_tree(yaml.safe_load(fh))

vault_cfg = CFG.get("vault", {})
file_cfg = vault_cfg.get("file", {})
if "path" in file_cfg:
    file_cfg["path"] = str((BASE_DIR / file_cfg["path"]).resolve())
    vault_cfg["file"] = file_cfg

catalog_cfg = CFG.get("catalog", {})
DEFAULT_ENV = catalog_cfg.get("default_env", "default")

rbac_cfg = CFG.get("rbac", {})
ROLE_PERMS: Dict[str, set[str]] = {
    role["name"].lower(): set(role.get("perms", [])) for role in rbac_cfg.get("roles", [])
}
DEFAULT_ROLE = rbac_cfg.get("default_role", "viewer").lower()

VAULT = Vault(vault_cfg)

DB_URL = os.getenv("DB_URL", "sqlite:///" + str((BASE_DIR / "aion_catalog.db").resolve()))
ENGINE = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, expire_on_commit=False)

metadata = MetaData()

categories = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("slug", String, unique=True, nullable=False),
    Column("title", String, nullable=False),
)

tools = Table(
    "tools",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True, nullable=False),
    Column("display_name", String, nullable=False),
    Column("category_id", Integer, ForeignKey("categories.id")),
    Column("pypi_name", String),
    Column("repo_url", String),
    Column("docs_url", String),
    Column("description", String),
    Column("latest_version", String),
    Column("license", String),
    Column("stars", Integer, server_default="0"),
    Column("tags", PG_ARRAY(String)),
    Column("config_schema", JSONB, server_default="'{}'::jsonb"),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)

tool_versions = Table(
    "tool_versions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tool_id", Integer, ForeignKey("tools.id", ondelete="CASCADE")),
    Column("version", String, nullable=False),
    Column("released_at", DateTime(timezone=True)),
    Column("yanked", Boolean, server_default="false"),
    Column("meta", JSONB),
)

installations = Table(
    "installations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tool_id", Integer, ForeignKey("tools.id", ondelete="CASCADE")),
    Column("env", String, nullable=False),
    Column("status", String, nullable=False),
    Column("version", String),
    Column("editable", Boolean, server_default="false"),
    Column("last_log", String),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)

jobs = Table(
    "jobs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("kind", String),
    Column("payload", JSONB),
    Column("status", String),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("finished_at", DateTime(timezone=True)),
)


app = FastAPI()


def get_session() -> Iterable[Session]:
    with SessionLocal() as session:
        yield session


def get_current_role(x_role: Optional[str] = Header(default=None)) -> str:
    role = (x_role or DEFAULT_ROLE).lower()
    if role not in ROLE_PERMS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed")
    return role


def require_perm(perm: str):
    def _dependency(role: str = Depends(get_current_role)) -> str:
        if perm not in ROLE_PERMS.get(role, set()):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return role

    return _dependency


def _category_title(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


@app.get("/catalog")
def list_catalog(
    category: Optional[str] = None,
    q: Optional[str] = None,
    session: Session = Depends(get_session),
    _role: str = Depends(require_perm("catalog.read")),
):
    stmt = (
        select(
            tools.c.name,
            tools.c.display_name,
            tools.c.description,
            tools.c.latest_version,
            tools.c.license,
            tools.c.tags,
            tools.c.docs_url,
            tools.c.repo_url,
            tools.c.config_schema,
            categories.c.slug.label("category"),
            categories.c.title.label("category_title"),
        )
        .select_from(tools.join(categories, tools.c.category_id == categories.c.id))
        .order_by(tools.c.display_name)
    )

    if category:
        stmt = stmt.where(categories.c.slug == category)

    if q:
        pattern = f"%{q}%"
        tags_field = func.array_to_string(tools.c.tags, " ")
        stmt = stmt.where(
            or_(
                tools.c.name.ilike(pattern),
                tools.c.display_name.ilike(pattern),
                tools.c.description.ilike(pattern),
                func.coalesce(tags_field, "").ilike(pattern),
            )
        )

    rows = session.execute(stmt).mappings().all()
    return {"items": [dict(row) for row in rows]}


@app.post("/catalog/upsert")
def upsert(
    payload: UpsertPayload,
    session: Session = Depends(get_session),
    _role: str = Depends(require_perm("catalog.read")),
):
    category_slug = payload.category
    tool_data = payload.tool
    category_title = tool_data.get("category_title") or _category_title(category_slug)

    cat_stmt = pg_insert(categories).values(slug=category_slug, title=category_title)
    cat_stmt = cat_stmt.on_conflict_do_update(
        index_elements=[categories.c.slug], set_={"title": category_title}
    ).returning(categories.c.id)
    category_id = session.execute(cat_stmt).scalar_one()

    tags = tool_data.get("tags") or []
    if isinstance(tags, tuple):
        tags = list(tags)

    tool_values = {
        "name": tool_data["name"],
        "display_name": tool_data.get("display_name")
        or tool_data["name"].replace("-", " ").title(),
        "category_id": category_id,
        "pypi_name": tool_data.get("pypi") or tool_data.get("pypi_name"),
        "repo_url": tool_data.get("repo") or tool_data.get("repo_url"),
        "docs_url": tool_data.get("docs") or tool_data.get("docs_url"),
        "description": tool_data.get("description"),
        "latest_version": tool_data.get("latest_version"),
        "license": tool_data.get("license"),
        "tags": tags,
        "config_schema": tool_data.get("config_schema", {}),
    }

    tool_stmt = pg_insert(tools).values(**tool_values)
    tool_stmt = tool_stmt.on_conflict_do_update(
        index_elements=[tools.c.name],
        set_={
            "display_name": tool_values["display_name"],
            "category_id": category_id,
            "pypi_name": tool_values["pypi_name"],
            "repo_url": tool_values["repo_url"],
            "docs_url": tool_values["docs_url"],
            "description": tool_values["description"],
            "latest_version": tool_values["latest_version"],
            "license": tool_values["license"],
            "tags": tool_values["tags"],
            "config_schema": tool_values["config_schema"],
            "updated_at": func.now(),
        },
    ).returning(tools)

    tool_row = session.execute(tool_stmt).mappings().one()
    session.commit()
    return {"ok": True, "tool": dict(tool_row)}


@app.post("/catalog/{name}/install")
def install_tool(
    name: str,
    req: InstallReq,
    session: Session = Depends(get_session),
    role: str = Depends(require_perm("install.run")),
):
    tool_row = (
        session.execute(select(tools).where(tools.c.name == name)).mappings().one_or_none()
    )
    if not tool_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    if req.editable and "install.editable" not in ROLE_PERMS.get(role, set()):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Editable install not allowed")

    target_env = req.env or DEFAULT_ENV
    version_value = req.version or tool_row.get("latest_version")

    result = install(
        name=name,
        env=target_env,
        version=req.version,
        editable=req.editable,
        repo_url=req.repo_url,
    )

    insert_stmt = pg_insert(installations).values(
        tool_id=tool_row["id"],
        env=target_env,
        status=result["status"],
        version=version_value,
        editable=req.editable,
        last_log=result.get("log"),
    )
    insert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[installations.c.tool_id, installations.c.env],
        set_={
            "status": result["status"],
            "version": version_value,
            "editable": req.editable,
            "last_log": result.get("log"),
            "updated_at": func.now(),
        },
    ).returning(installations)
    install_row = session.execute(insert_stmt).mappings().one()
    session.commit()
    return {"status": result["status"], "log": result.get("log"), "installation": dict(install_row)}


@app.post("/catalog/{name}/config")
def save_config(
    name: str,
    body: SaveConfigReq,
    role: str = Depends(require_perm("vault.write")),
):
    path = f"aion/{body.env or DEFAULT_ENV}/{name}"
    VAULT.put(path, body.config)
    logger.info("vault.put", extra={"tool": name, "env": body.env, "role": role})
    return {"ok": True}


@app.get("/catalog/{name}/config")
def read_config(
    name: str,
    env: Optional[str] = None,
    role: str = Depends(require_perm("vault.read")),
):
    path = f"aion/{env or DEFAULT_ENV}/{name}"
    data = VAULT.get(path)
    logger.info("vault.get", extra={"tool": name, "env": env or DEFAULT_ENV, "role": role})
    return data
