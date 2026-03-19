"""Thin wrapper around litellm for text completion.

Configure via environment variables:
  LLM_MODEL    — litellm model string, e.g. "ollama/qwen2:7b" (default)
  OLLAMA_HOST  — Ollama base URL, e.g. "http://ollama:11434" (default: localhost)
"""
import os
from typing import Optional

import litellm

litellm.suppress_debug_info = True


def complete(prompt: str, max_tokens: int = 500) -> str:
    """Call the configured LLM and return the response as a plain string."""
    model = os.getenv("LLM_MODEL", "ollama/qwen2:7b")
    kwargs: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    if model.startswith("ollama/"):
        kwargs["api_base"] = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    resp = litellm.completion(**kwargs)
    content: Optional[str] = resp.choices[0].message.content
    return content or ""
