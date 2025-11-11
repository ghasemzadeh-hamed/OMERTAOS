from __future__ import annotations

import requests

from .config import settings


def fetch_self_edits() -> list[dict]:
    url = f"{settings.MEMORY_URL}/self-edits/top"
    params = {"min_reward": settings.MIN_REWARD, "limit": settings.MAX_EDITS}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def build_sft_dataset(edits: list[dict]) -> list[dict]:
    samples: list[dict] = []
    for edit in edits:
        interaction_id = edit["interaction_id"]
        interaction_response = requests.get(
            f"{settings.MEMORY_URL}/interactions/{interaction_id}", timeout=10
        )
        interaction_response.raise_for_status()
        interaction = interaction_response.json()
        prompt = interaction.get("input_text", "")
        response_text = edit.get("edited_output", "")
        if prompt and response_text:
            samples.append({"prompt": prompt, "response": response_text})
    return samples
