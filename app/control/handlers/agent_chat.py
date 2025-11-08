"""Agent Chat handler that orchestrates tool-augmented conversations."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Iterable, List, Mapping

from app.control.tools import FileReadTool, HttpGetTool, RagSearchTool, ShellTool
from app.kernel.engines import OllamaChat, OpenAIChat, PhiMini, VLLMChat

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import redis  # type: ignore
except Exception:  # pragma: no cover - redis is optional
    redis = None  # type: ignore

MEMORY_KEY_PREFIX = "agent:chat:"
DEFAULT_MEMORY_TTL = int(os.getenv("AION_AGENT_MEMORY_TTL", "2592000"))
MAX_HISTORY_MESSAGES = 12
MAX_MEMORY_MESSAGES = 50
MAX_SCRATCHPAD_CHARS = 4000

_SYSTEM_PROMPT = (
    "You are Agent Chat. Use tools to complete the user's task.\n"
    "Respond in the user's language. Chain-of-thought is private: only share conclusions.\n"
    "Format:\n"
    "THOUGHT: ...\n"
    'ACTION: {"tool":"name","args":{...}}\n'
    "OBSERVATION: ...\n"
    "FINAL: <answer to user>"
)

_TOOLS = {
    "rag.search": RagSearchTool(),
    "file.read": FileReadTool(allow_dirs=["/data", "/app/shared"]),
    "ops.shell": ShellTool(allow=["ls", "du", "df", "cat", "head", "tail"]),
    "http.get": HttpGetTool(allow_domains=["example.com", "docs.company.local"]),
}

_redis_client = None
if redis is not None:
    redis_url = os.getenv("AION_REDIS_URL") or os.getenv("REDIS_URL")
    if redis_url:
        try:
            _redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        except Exception:  # pragma: no cover - logging only
            logger.warning("Failed to connect to Redis for agent memory", exc_info=True)

_fallback_memory: dict[str, tuple[float, List[Dict[str, str]]]] = {}


def _memory_key(session_id: str) -> str:
    return f"{MEMORY_KEY_PREFIX}{session_id}"


def _load_memory(session_id: str) -> List[Dict[str, str]]:
    if not session_id:
        return []
    if _redis_client is not None:
        try:
            payload = _redis_client.get(_memory_key(session_id))
            if payload:
                data = json.loads(payload)
                if isinstance(data, list):
                    return [
                        {"role": str(item.get("role", "")), "content": str(item.get("content", ""))}
                        for item in data
                        if isinstance(item, Mapping)
                    ]
        except Exception:  # pragma: no cover - logging only
            logger.warning("Failed to load conversation memory from Redis", exc_info=True)
    now = time.time()
    stored = _fallback_memory.get(session_id)
    if not stored:
        return []
    expires_at, history = stored
    if now > expires_at:
        _fallback_memory.pop(session_id, None)
        return []
    return history.copy()


def _save_memory(session_id: str, history: List[Dict[str, str]]) -> None:
    if not session_id or not history:
        return
    trimmed = history[-MAX_MEMORY_MESSAGES:]
    payload = json.dumps(trimmed, ensure_ascii=False)
    if _redis_client is not None:
        try:
            _redis_client.setex(_memory_key(session_id), DEFAULT_MEMORY_TTL, payload)
            return
        except Exception:  # pragma: no cover - logging only
            logger.warning("Failed to persist conversation memory to Redis", exc_info=True)
    _fallback_memory[session_id] = (time.time() + DEFAULT_MEMORY_TTL, trimmed)


def _normalise_history(messages: Any) -> List[Dict[str, str]]:
    normalised: List[Dict[str, str]] = []
    if not isinstance(messages, list):
        return normalised
    for item in messages:
        if not isinstance(item, Mapping):
            continue
        role = str(item.get("role", "")).strip() or "assistant"
        content = str(item.get("content", ""))
        normalised.append({"role": role, "content": content})
    return normalised


def _build_prompt(history: List[Dict[str, str]], scratchpad: str) -> List[Dict[str, str]]:
    prompt: List[Dict[str, str]] = [{"role": "system", "content": _SYSTEM_PROMPT}]
    prompt.extend(history[-MAX_HISTORY_MESSAGES:])
    if scratchpad:
        prompt.append({"role": "system", "content": f"Scratchpad:\n{scratchpad}"})
    return prompt


def _parse_model_override(raw: str) -> tuple[str | None, str | None]:
    raw = raw.strip()
    if not raw:
        return None, None
    if ":" in raw:
        provider, model = raw.split(":", 1)
        return provider or None, model or None
    return None, raw


def resolve_llm():
    """Resolve an LLM backend using the configured fallbacks."""

    override_provider, override_model = _parse_model_override(os.getenv("AION_AGENT_MODEL", ""))
    providers = [
        ("openai", OpenAIChat, "gpt-4.5"),
        ("ollama", OllamaChat, "qwen2.5:7b"),
        ("vllm", VLLMChat, "llama-3.2-3b-instruct"),
        ("local", PhiMini, "phi-3-mini"),
    ]
    errors: list[str] = []

    def _instantiate(provider: str, factory, model_hint: str):
        model_name = override_model or model_hint
        if provider == "openai" and factory.is_available():
            return factory(model=model_name, temperature=0.2)
        if provider == "ollama" and factory.is_available():
            return factory(model=model_name, temperature=0.2)
        if provider == "vllm" and factory.is_available():
            return factory(model=model_name, temperature=0.2)
        if provider == "local":
            return factory()
        raise RuntimeError("provider unavailable")

    ordered = providers
    if override_provider:
        ordered = sorted(providers, key=lambda item: 0 if item[0] == override_provider else 1)

    for provider, factory, model_hint in ordered:
        try:
            llm = _instantiate(provider, factory, model_hint)
            logger.info("Resolved agent chat model", extra={"provider": provider, "model": getattr(llm, "model", getattr(llm, "name", "unknown"))})
            return llm
        except Exception as exc:  # pragma: no cover - runtime dependent
            errors.append(f"{provider}: {exc}")
            continue

    raise RuntimeError(f"No LLM backend available. Details: {errors}")


def _extract_action(block: str) -> Dict[str, Any] | None:
    if "{" not in block:
        return None
    candidate = block
    closing = block.find("}")
    if closing != -1:
        candidate = block[: closing + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        try:
            closing = block.rfind("}")
            if closing != -1:
                return json.loads(block[: closing + 1])
        except json.JSONDecodeError:
            return None
    except Exception:
        return None
    return None


def handle_agent_chat(task: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    """Main entry point executed by the control plane orchestrator."""

    params = task.get("params", {}) or {}
    session_id = str(
        params.get("session_id")
        or task.get("session_id")
        or task.get("task_id")
        or ""
    )
    auto_confirm = bool(params.get("auto_confirm") or params.get("autoConfirm"))
    history = _normalise_history(params.get("history"))
    if session_id and not params.get("history"):
        persisted = _load_memory(session_id)
        if persisted:
            history = persisted
    user_message = str(params.get("message", ""))
    if user_message:
        history.append({"role": "user", "content": user_message})

    try:
        llm = resolve_llm()
    except Exception as exc:
        error_msg = f"مدل در دسترس نیست: {exc}"
        logger.error("Agent chat failed to resolve LLM", exc_info=True)
        yield {"text": error_msg, "status": "ERROR"}
        return

    scratchpad = ""
    steps = 0
    partial_buffer = ""

    while steps < 6:
        steps += 1
        prompt = _build_prompt(history, scratchpad)
        try:
            response_text = llm.complete(prompt)
        except Exception as exc:
            logger.exception("Agent chat model invocation failed")
            yield {"text": f"خطا در فراخوانی مدل: {exc}", "status": "ERROR"}
            return

        text = response_text if isinstance(response_text, str) else json.dumps(response_text)

        if "FINAL:" in text:
            final = text.split("FINAL:", 1)[1].strip()
            history.append({"role": "assistant", "content": final})
            if session_id:
                _save_memory(session_id, history)
            yield {"text": final, "status": "OK"}
            return

        if "ACTION:" in text:
            action_block = text.split("ACTION:", 1)[1].strip()
            action = _extract_action(action_block)
            if not action:
                history.append({"role": "assistant", "content": "خطا در ACTION. لطفاً مجدد تلاش کنید."})
                yield {"delta": "خطا در ACTION. لطفاً مجدد تلاش کنید."}
                continue
            tool_name = str(action.get("tool", ""))
            args = action.get("args") or {}
            tool = _TOOLS.get(tool_name)
            if not tool:
                message = f"ابزاری با نام {tool_name} در دسترس نیست."
                history.append({"role": "assistant", "content": message})
                yield {"delta": message}
                continue
            if tool_name.startswith("ops.") and not auto_confirm:
                prompt_msg = f"پیش از اجرای {tool_name} با args={args} تایید می‌کنی؟ (yes/no)"
                history.append({"role": "assistant", "content": prompt_msg})
                if session_id:
                    _save_memory(session_id, history)
                yield {"text": prompt_msg, "status": "OK"}
                return
            try:
                observation = tool.run(**args)
            except Exception as exc:  # pragma: no cover - runtime dependent
                observation = f"اجرای ابزار با خطا مواجه شد: {exc}"
            scratchpad += f"\nACTION: {tool_name} {json.dumps(args, ensure_ascii=False)}\nOBSERVATION: {observation[:2000]}"
            if len(scratchpad) > MAX_SCRATCHPAD_CHARS:
                scratchpad = scratchpad[-MAX_SCRATCHPAD_CHARS:]
            history.append({"role": "assistant", "content": f"OBSERVATION: {observation[:300]}"})
            continue

        if text.strip():
            partial_buffer += text
            history.append({"role": "assistant", "content": text})
            yield {"delta": text}
            if len(partial_buffer) > 1800:
                clarification = "لطفاً مشخص کن چه کاری می‌خواهی انجام شود."
                history.append({"role": "assistant", "content": clarification})
                yield {"text": clarification, "status": "OK"}
                if session_id:
                    _save_memory(session_id, history)
                return

    fallback = partial_buffer or "پایان گفتگو."
    history.append({"role": "assistant", "content": fallback})
    if session_id:
        _save_memory(session_id, history)
    yield {"text": fallback, "status": "OK"}
