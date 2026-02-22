"""Dev kernel implementation using orchestrator and Qwen coder."""

from __future__ import annotations

from typing import Any, Dict

from app.config.profiles import load_profile_config
from app.llm.client import LLMProviderDisabled, call_llm
from app.utils.context import load_relevant_context
from app.utils.json_utils import safe_json_parse

_CFG = load_profile_config("dev-qwen-coder")

_ORCH_SYSTEM = """
You are the Dev Kernel Orchestrator.
Decide ONLY routing for the user's request to AION-OS Dev Kernel.

Rules:
- Identify if the request is a CODE_TASK or NON_CODE_TASK.
- For CODE_TASK, you MUST output JSON:
  {
    "route": "coder",
    "targets": ["paths or modules to touch"],
    "instructions": "precise coding instructions for the code engine",
    "tests_required": true/false
  }
- For NON_CODE_TASK, you MUST output JSON:
  {
    "route": "orchestrator",
    "intent": "short description of what explanation/design is requested"
  }
- No prose. No comments. Only valid JSON.
""".strip()

_CODER_SYSTEM = """
You are Qwen2.5-Coder, the ONLY code engine for the AION-OS Dev Kernel.

Requirements:
- Operate strictly on an existing repository (OMERTAOS/AION-OS).
- Generate COMPLETE, EXECUTABLE code or patches. No placeholders, no pseudo-code.
- When modifying files, show them either as full file contents or unified patches.
- Preserve architecture, module boundaries, and naming used in the repo.
- Do not create services not wired in compose/pyproject unless explicitly asked.
- Be deterministic, minimal, and explicit.
""".strip()


def _offline_route(user_msg: str) -> Dict[str, Any]:
    fallback = _CFG.get("fallback", {})
    patterns = fallback.get("offline_patterns", {})
    code_keywords = [value.lower() for value in patterns.get("code_keywords", [])]
    doc_keywords = [value.lower() for value in patterns.get("doc_keywords", [])]

    lowered = user_msg.lower()
    code_match = any(keyword in lowered for keyword in code_keywords)
    doc_match = any(keyword in lowered for keyword in doc_keywords)

    if code_match and not doc_match:
        return {
            "route": "coder",
            "targets": [],
            "instructions": "User request is code-related. Generate a minimal, safe patch.",
            "tests_required": True,
        }

    return {
        "route": "orchestrator",
        "intent": "Non-code or documentation/architecture style request.",
    }


def _build_coder_prompt(user_msg: str, spec: Dict[str, Any], context: str) -> str:
    return (
        "User request:\n"
        f"{user_msg}\n\n"
        "Routing spec:\n"
        f"{spec}\n\n"
        "Relevant repository context (read-only, do not restate blindly):\n"
        f"{context}\n\n"
        "Now produce final, ready-to-apply patches or file contents only."
    )


def _route_request(user_msg: str) -> Dict[str, Any]:
    orchestrator_cfg = _CFG.get("orchestrator", {})
    try:
        if orchestrator_cfg.get("enabled", False):
            orchestrator_reply = call_llm(
                orchestrator_cfg,
                system=_ORCH_SYSTEM,
                messages=[{"role": "user", "content": user_msg}],
                max_tokens=512,
                temperature=0.2,
            )
            parsed = safe_json_parse(orchestrator_reply)
            return parsed or {}
        raise LLMProviderDisabled("orchestrator disabled by config")
    except (LLMProviderDisabled, Exception):
        if _CFG.get("fallback", {}).get("offline_router_enabled", True):
            return _offline_route(user_msg)
        return {"route": "coder", "instructions": user_msg, "targets": []}


def dev_kernel_handle(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a kernel invocation using the dev profile."""

    user_msg = request.get("message", "")
    if not user_msg:
        return {"type": "error", "content": "Empty request."}

    repo_context = load_relevant_context(user_msg)
    route_spec = _route_request(user_msg)
    route = route_spec.get("route", "coder")

    if route == "orchestrator":
        orchestrator_cfg = _CFG.get("orchestrator", {})
        try:
            if not orchestrator_cfg.get("enabled", False):
                raise LLMProviderDisabled("orchestrator disabled by config")
            explanation = call_llm(
                orchestrator_cfg,
                system="You are a concise, accurate AION-OS software architect.",
                messages=[{"role": "user", "content": user_msg}],
                max_tokens=1024,
                temperature=0.3,
            )
            return {"type": "text", "content": explanation}
        except (LLMProviderDisabled, Exception):
            return {
                "type": "text",
                "content": (
                    "Dev Kernel: orchestrator model unavailable. "
                    "This request was classified as NON_CODE_TASK. "
                    "No code patch generated."
                ),
            }

    coder_cfg = _CFG.get("coder", {})
    coder_input = _build_coder_prompt(user_msg, route_spec, repo_context)

    try:
        if not coder_cfg.get("enabled", False):
            raise LLMProviderDisabled("coder disabled by config")
        coder_reply = call_llm(
            coder_cfg,
            system=_CODER_SYSTEM,
            messages=[{"role": "user", "content": coder_input}],
            max_tokens=4096,
            temperature=0.15,
        )
        return {"type": "patch", "content": coder_reply}
    except (LLMProviderDisabled, Exception):
        fallback = _CFG.get("fallback", {})
        behavior = fallback.get("on_coder_unavailable", "return_explained_plan")
        if behavior == "return_error":
            return {
                "type": "error",
                "content": (
                    "Dev Kernel: code engine (Qwen2.5-Coder) is unavailable. "
                    "Cannot safely generate patches."
                ),
            }
        return {
            "type": "plan",
            "content": (
                "Dev Kernel: Qwen2.5-Coder is unavailable. "
                "Below is a precise implementation plan for the required changes. "
                "Apply manually or when the code engine is back:\n\n"
                f"{coder_input}"
            ),
        }


__all__ = ["dev_kernel_handle"]
