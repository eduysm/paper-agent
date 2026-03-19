# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run the legacy agentic reader (from readerAI/)
poetry run python readerAI/agent.py

# Run the newsletter CLI (from src/doctorate_reader/)
poetry run python -m doctorate_reader.cli "política económica" --top-n 5 --num-results 20

# Redirect HTML output to file
poetry run python -m doctorate_reader.cli "tema" > newsletter.html
```

The project uses Poetry for dependency management (`pyproject.toml`). There are no automated tests beyond the scripts in `tests/`.

## Architecture

There are two parallel implementations:

### `readerAI/` — legacy agentic approach
A `smolagents` `CodeAgent` that receives a topic, calls the `search_papers` tool against OpenAlex, and returns structured results. The LLM backend is selected via the `MODEL_BACKEND` env var (`ollama` by default, `hf` for HuggingFace). System/user prompts are loaded from `readerAI/prompts/system.yaml`.

### `src/doctorate_reader/` — newsletter pipeline (current main package)
A four-stage pipeline with no agent loop:

1. **`skills/search.py`** — wraps `readerAI/tools/OpenAlex_searcher.py` and converts raw dicts into `Paper` objects (`schemas.py`).
2. **`skills/filtering.py`** — filters by year/open-access and ranks by citations desc.
3. **`skills/summarization.py`** — uses a minimal `CodeAgent` (no tools) via `get_model()` to generate a short summary for each paper.
4. **`skills/composition.py`** — assembles everything into an HTML newsletter string.

The `workflows/newsletter.py` orchestrates these four skills and is the entry point called by `cli.py`.

### Shared infrastructure
- **`readerAI/tools/OpenAlex_searcher.py`** — the only data source; calls the OpenAlex REST API (no API key required). Reconstructs abstracts from OpenAlex's inverted-index format.
- **`readerAI/llm_conect/`** — model factory; `get_model()` returns a `LiteLLMModel` wrapping either Ollama (`qwen2:7b`) or HuggingFace depending on `MODEL_BACKEND`.
- **`src/doctorate_reader/schemas.py`** — plain `Paper` dataclass (no Pydantic) shared across all skills.

### Key dependency note
`src/doctorate_reader/skills/search.py` and `skills/summarization.py` import directly from `readerAI/`, so both packages must be on the Python path simultaneously. When running via `poetry run`, this works because both directories are in the project root.
