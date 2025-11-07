from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yaml, os, secrets, subprocess

from os.control.os.config_paths import resolve_config_path

router = APIRouter(prefix="/admin/onboarding", tags=["admin"])

def _config_path(prefer_existing: bool = True) -> str:
    return str(resolve_config_path(prefer_existing=prefer_existing))
ENV_OUT = os.getenv("AIONOS_ENV_OUT", "/app/.env")

class SubmitPayload(BaseModel):
    stepId: str
    answers: dict

@router.get("/status")
def status():
    try:
        with open(_config_path(), "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return {"onboardingComplete": bool(cfg.get("onboardingComplete", False))}
    except FileNotFoundError:
        return {"onboardingComplete": False}

@router.post("/submit")
def submit(p: SubmitPayload):
    try:
        config_path = _config_path(prefer_existing=False)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        cfg = {}
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

        if p.stepId == "admin":
            email = (p.answers.get("email") or "").strip()
            password = (p.answers.get("password") or "").strip()
            if not email or not password:
                raise HTTPException(400, "admin email/password required")
            if "@" not in email:
                email = f"{email}@localhost"
            cfg.setdefault("admin", {})["email"] = email
            cfg["admin"]["password"] = password

        elif p.stepId == "models":
            provider = (p.answers.get("provider") or "openai").strip()
            apiKey = p.answers.get("apiKey") or ""
            defaultModel = (p.answers.get("defaultModel") or "gpt-4o-mini").strip()
            cfg.setdefault("models", {})
            cfg["models"].update({
                "provider": provider,
                "openaiApiKey": apiKey if provider == "openai" else "",
                "defaultModel": defaultModel,
            })

        elif p.stepId == "gateway":
            port = int(p.answers.get("port") or 8080)
            apiKey = p.answers.get("apiKey") or secrets.token_hex(16)
            cfg.setdefault("gateway", {})
            cfg["gateway"].update({"port": port, "apiKey": apiKey})

        # finalize: defer console/admin provisioning to /apply handler

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)

        return {"ok": True}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, f"submit failed: {e}")

def render_env_from_yaml(cfg: dict) -> str:
    out = []
    out.append(f"NEXTAUTH_SECRET={secrets.token_hex(32)}")
    out.append(f"CONSOLE_BASE_URL={cfg.get('console',{}).get('baseUrl','http://localhost:3000')}")
    out.append(f"GATEWAY_PORT={cfg.get('gateway',{}).get('port',8080)}")
    out.append(f"GATEWAY_API_KEY={cfg.get('gateway',{}).get('apiKey','')}")
    out.append(f"CONTROL_HTTP_PORT={cfg.get('control',{}).get('httpPort',8000)}")
    out.append(f"OPENAI_API_KEY={cfg.get('models',{}).get('openaiApiKey','')}")
    # TODO: expose Redis/Qdrant/MinIO/DB/Telemetry env rendering when needed
    return "\n".join(out) + "\n"

@router.post("/apply")
def apply():
    try:
        with open(_config_path(), "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        # 1) render .env from YAML (control/gateway/console)
        env_text = render_env_from_yaml(cfg)
        with open(ENV_OUT, "w", encoding="utf-8") as f:
            f.write(env_text)

        # 2) Optionally invoke provisioning endpoints/scripts here
        # subprocess.run(["python","/app/scripts/create_admin.py", cfg["admin"]["email"], cfg["admin"]["password"]], check=False)

        # 3) scrub secrets from YAML for post-onboarding state
        if "admin" in cfg and "password" in cfg["admin"]:
            cfg["admin"]["password"] = ""
        cfg["onboardingComplete"] = True
        with open(_config_path(prefer_existing=False), "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)

        # 4) In production you may restart orchestrators or services here
        # if os.getenv("IN_DOCKER","1") == "1":
        #     subprocess.run(["/usr/bin/docker","compose","restart"], check=False)

        return {"ok": True, "reloaded": True}
    except Exception as e:
        raise HTTPException(500, f"apply failed: {e}")
