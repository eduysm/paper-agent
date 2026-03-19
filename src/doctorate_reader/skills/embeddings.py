import math
import os
from typing import List, Optional

import requests


_EMBED_MODEL = "nomic-embed-text"


def _ollama_url() -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    return f"{host}/api/embeddings"


def _embed(text: str, timeout: int = 30) -> List[float]:
    url = _ollama_url()
    try:
        resp = requests.post(
            url,
            json={"model": _EMBED_MODEL, "prompt": text},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]
    except requests.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {url}. "
            "Ensure Ollama is running and the model is pulled: "
            f"ollama pull {_EMBED_MODEL}"
        )
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Ollama returned HTTP {exc.response.status_code} for model '{_EMBED_MODEL}'. "
            f"Pull the model with: ollama pull {_EMBED_MODEL}"
        ) from exc


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def build_user_vector(
    interests: List[str],
    research_line: Optional[str] = None,
    example_docs: Optional[List[str]] = None,
    topic: Optional[str] = None,
) -> List[float]:
    parts: List[str] = []
    if topic:
        parts.append(topic)
    parts.extend(interests)
    if research_line:
        parts.append(research_line)
    if example_docs:
        parts.extend(example_docs)
    combined = "\n".join(parts)
    return _embed(combined)


def embed_paper(title: str, abstract: Optional[str]) -> List[float]:
    text = f"{title} {abstract}" if abstract else title
    return _embed(text)


def score_paper(paper_vector: List[float], user_vector: List[float]) -> float:
    return _cosine_similarity(paper_vector, user_vector)
