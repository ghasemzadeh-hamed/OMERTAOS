import os
from typing import Any, Dict, List

import httpx

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
VLLM_HOST = os.getenv("VLLM_HOST", "http://127.0.0.1:8008")  # default from docker-compose.vllm.yml


class LocalLLM:
    def __init__(self, model: str, engine: str = "ollama", ctx: int = 4096, temperature: float = 0.2):
        self.model = model
        self.engine = engine
        self.ctx = ctx
        self.temperature = temperature

    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        if self.engine == "vllm":
            return self._chat_vllm(messages, stream=stream)
        return self._chat_ollama(messages, stream=stream)

    def _chat_ollama(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        url = f"{OLLAMA_HOST}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "options": {
                "num_ctx": self.ctx,
                "temperature": self.temperature,
            },
            "stream": stream,
        }
        with httpx.Client(timeout=180.0) as client:
            response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        message = data.get("message") or {}
        return message.get("content", "")

    def _chat_vllm(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        # vLLM OpenAI-compatible
        url = f"{VLLM_HOST}/v1/chat/completions"
        payload = {
            "model": "local",  # vLLM ignores this if only a single model is loaded
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 1024,
            "stream": stream,
        }
        with httpx.Client(timeout=180.0) as client:
            response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
