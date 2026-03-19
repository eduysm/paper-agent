# Architecture & File Guide

## Overview

The project has two parallel implementations that share a common data source:

- **`readerAI/`** — legacy agentic approach (smolagents loop)
- **`src/doctorate_reader/`** — newsletter pipeline (current main package)

Both rely on the same OpenAlex REST API tool as their only data source.

---

## Data flow

### Newsletter pipeline (`src/doctorate_reader/`)

```
CLI invocation
    │
    ▼
cli.py                          parse args, load user profile if --profile
    │
    ▼
workflows/newsletter.py         orchestration: calls each skill in order
    │
    ├─► [optional] skills/embeddings.py   build_user_vector()
    │                                      embeds all profile text into one vector
    │
    ├─► skills/search.py                  search_papers_skill()
    │       └─► readerAI/tools/OpenAlex_searcher.py  HTTP → OpenAlex API
    │           returns raw dicts
    │       converts raw dicts → List[Paper]
    │
    ├─► skills/filtering.py               filter_and_rank_papers()
    │       if user_vector:  embed each paper → cosine sim → rank desc
    │       else:            rank by citations desc, year desc
    │
    ├─► skills/summarization.py           summarize_paper() per paper
    │       └─► readerAI/llm_conect/base.py  get_model() → LiteLLMModel
    │           runs a minimal CodeAgent (no tools) → short summary string
    │
    └─► skills/composition.py             compose_newsletter_html()
            assembles Paper objects + summaries → HTML string
    │
    ▼
stdout  (redirect to file with >)
```

### Legacy agent (`readerAI/`)

```
readerAI/agent.py
    │
    ├─► prompts/system.yaml              loads system + user prompts
    ├─► llm_conect/base.py               get_model() selects Ollama or HF backend
    └─► tools/OpenAlex_searcher.py       search_papers() registered as smolagents @tool
    │
    ▼
CodeAgent.run()  (max_steps=1)          LLM calls search_papers, returns structured result
```

---

## File-by-file reference

### `src/doctorate_reader/`

| File | Purpose |
|---|---|
| `cli.py` | Entry point. Parses CLI args (`topic`, `--top-n`, `--num-results`, `--min-year`, `--only-open-access`, `--profile`, `--setup-profile`). Loads `UserProfile` if `--profile` is given. Calls `build_newsletter_html` and prints HTML to stdout. |
| `schemas.py` | Plain Python dataclasses shared across the whole package. `Paper` holds all metadata for one academic paper. `UserProfile` holds a researcher's interests, research line description, and example document excerpts. No Pydantic. |
| `workflows/newsletter.py` | Orchestrator. Calls the four skills in sequence. Builds the user embedding vector once (if a profile is provided) before filtering. Degrades gracefully to citation ranking if Ollama is unreachable. |
| `skills/search.py` | Thin adapter. Calls `readerAI/tools/OpenAlex_searcher.search_papers()` and converts the raw dict list into `List[Paper]`. Natural place to add caching or a vector store later. |
| `skills/filtering.py` | Filters papers by `min_year` and `open_access`. Then sorts: by cosine similarity to `user_vector` (desc) when provided, or by citations/year otherwise. Embedding errors per paper → `warnings.warn` + fallback score `0.0`. |
| `skills/summarization.py` | Creates a minimal `CodeAgent` (no tools) for each paper and asks the LLM to write a short newsletter-style summary in Spanish. Length controlled by `max_words`. |
| `skills/composition.py` | Pure string assembly. Takes lists of `(Paper, summary)` tuples and renders them into a self-contained HTML newsletter with inline CSS. |
| `skills/embeddings.py` | HTTP client for the Ollama embedding endpoint (`nomic-embed-text`). Provides `build_user_vector`, `embed_paper`, `score_paper`, and `_cosine_similarity`. No new dependencies (`requests` already declared). Raises `RuntimeError` with actionable messages on connection/HTTP failures. |
| `skills/user_profile.py` | Profile persistence. `load_profile(path)` reads YAML → `UserProfile`. `save_profile(profile, path)` writes YAML. `setup_profile_interactive()` runs an `input()`-based wizard to collect interests, research line, and example excerpts. |

---

### `readerAI/`

| File | Purpose |
|---|---|
| `agent.py` | Entry point for the legacy approach. Loads prompts from YAML, instantiates a `smolagents.CodeAgent` with `search_papers` as tool, and runs it once for a given topic. |
| `tools/OpenAlex_searcher.py` | The **only data source** in the project. Calls the OpenAlex REST API (no key needed). Handles date filters, journal filters, and reconstructs full abstracts from OpenAlex's inverted-index format. Decorated with `@tool` for smolagents compatibility. Also called directly by `skills/search.py`. |
| `tools/scholar_searcher_extra.py` | Unused/experimental searcher. Not integrated into either pipeline. |
| `llm_conect/base.py` | `get_model()` factory. Reads `MODEL_BACKEND` env var (`ollama` default, `hf` for HuggingFace) and returns the appropriate `LiteLLMModel`. Used by both the legacy agent and `skills/summarization.py`. |
| `llm_conect/ollama.py` | Returns a `LiteLLMModel` pointing at `qwen2:7b` via Ollama. |
| `llm_conect/huggingface.py` | Returns a `LiteLLMModel` pointing at a HuggingFace model. |
| `schemas.py` | Legacy schemas (separate from `src/doctorate_reader/schemas.py`). Not actively used by the newsletter pipeline. |

---

### `tests/`

| File | Purpose |
|---|---|
| `test_user_profile.py` | Save/load roundtrip for `UserProfile`. Covers full profile, minimal profile, missing file, and malformed YAML. No external services needed. |
| `test_embeddings.py` | Verifies that semantically related texts score higher than unrelated ones. **Requires Ollama running** with `nomic-embed-text` pulled. Also tests edge cases (`_cosine_similarity` with zero vectors). |
| `testing_ollama.py` | Ad-hoc script to verify the Ollama connection manually. |
| `testing_scholar_search.py` | Ad-hoc script to test the OpenAlex searcher directly. |

---

## Key dependency note

`skills/search.py` and `skills/summarization.py` import directly from `readerAI/`. Both directories must be on `sys.path` simultaneously. When running via `poetry run`, this works automatically because both `src/` and the project root are on the path.

---

## Environment variables

| Variable | Default | Effect |
|---|---|---|
| `MODEL_BACKEND` | `ollama` | Set to `hf` to use HuggingFace instead of Ollama for summarization |

---

## Quick-start commands

```bash
# Install
poetry install

# One-time: pull embedding model (~274 MB)
ollama pull nomic-embed-text

# Create user profile interactively
poetry run python -m doctorate_reader.cli --setup-profile ~/.doctorate_reader/profile.yaml

# Run with semantic ranking
poetry run python -m doctorate_reader.cli "política fiscal" \
    --profile ~/.doctorate_reader/profile.yaml > newsletter.html

# Run without profile (citation-based ranking)
poetry run python -m doctorate_reader.cli "política fiscal" --top-n 5 --num-results 20 > newsletter.html

# Run legacy agent
poetry run python readerAI/agent.py

# Run tests
poetry run pytest tests/test_user_profile.py tests/test_embeddings.py -v
```
