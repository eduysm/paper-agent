FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Copy dependency files first (layer cache)
COPY pyproject.toml poetry.lock* ./

# Install dependencies into the system Python (no virtualenv needed in Docker)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy source and install the package itself
COPY src/ ./src/
RUN poetry install --no-interaction --no-ansi --only-root

EXPOSE 8000

CMD ["uvicorn", "doctorate_reader.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
