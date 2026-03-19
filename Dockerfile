FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir "poetry>=2.0.0,<3.0.0"

# Copy dependency files first (layer cache: invalidated only if lock changes)
COPY pyproject.toml poetry.lock* ./

# Install deps only — no root package yet
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Copy source and install the package itself (no-deps: already installed above)
COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps .

EXPOSE 8000

CMD ["uvicorn", "doctorate_reader.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
