# Doctorate Reader

Genera newsletters académicas personalizadas buscando papers en **OpenAlex** y resumiéndolos con un LLM local (**Ollama**). El ranking puede ser por citas o por similitud semántica a un perfil de investigador.

## Stack

- Python 3.12 · Poetry
- [OpenAlex](https://openalex.org/) — fuente de datos (sin API key)
- [Ollama](https://ollama.com/) — LLM local y embeddings (gratuito, sin cuenta)
- FastAPI + SQLite — API REST para integración con frontend
- Docker + Docker Compose — despliegue en un comando

---

## Opción A — Docker (recomendado)

La forma más rápida. Solo necesitas Docker Desktop instalado.

```bash
# 1. Clona el repo
git clone https://github.com/eduysm/paper-agent.git
cd paper-agent

# 2. Levanta los servicios (construye la imagen + arranca Ollama)
docker compose up --build
```

La primera vez Ollama descarga automáticamente los dos modelos necesarios:
- `qwen2:7b` (~4 GB) — generación de resúmenes
- `nomic-embed-text` (~274 MB) — embeddings para ranking semántico

Cuando veas `Application startup complete` la API está lista:

```
API:   http://localhost:8000
Docs:  http://localhost:8000/docs
```

Para parar:
```bash
docker compose down
```

---

## Opción B — Local con Poetry

### Requisitos previos

1. [Python 3.12+](https://www.python.org/downloads/)
2. [Poetry](https://python-poetry.org/docs/#installation)
3. [Ollama](https://ollama.com/download) instalado y corriendo

### Instalación

```bash
git clone https://github.com/eduysm/paper-agent.git
cd paper-agent
poetry install
```

### Descargar modelos de Ollama

```bash
ollama pull qwen2:7b          # LLM para resúmenes (~4 GB)
ollama pull nomic-embed-text  # Embeddings (~274 MB)
```

### Levantar la API

```bash
poetry run uvicorn doctorate_reader.api.main:app --reload
```

API disponible en `http://localhost:8000` · Docs en `http://localhost:8000/docs`

---

## Uso de la API

### 1. Crear un perfil de investigador

```bash
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["fiscal policy", "inequality", "public spending"],
    "research_line": "Estudio cómo las transferencias del gobierno afectan la distribución del ingreso.",
    "example_docs": ["Excerpt from my paper on fiscal multipliers..."]
  }'
```

Respuesta:
```json
{ "id": "uuid-del-perfil", "interests": [...], ... }
```

### 2. Generar una newsletter

```bash
# Sin perfil (ranking por citas)
curl -X POST http://localhost:8000/api/v1/newsletters \
  -H "Content-Type: application/json" \
  -d '{"topic": "política fiscal", "top_n": 5, "num_results": 20}'

# Con perfil (ranking semántico)
curl -X POST http://localhost:8000/api/v1/newsletters \
  -H "Content-Type: application/json" \
  -d '{"topic": "política fiscal", "profile_id": "uuid-del-perfil", "top_n": 5}'
```

Ambos devuelven un `job_id` inmediatamente (la generación es asíncrona):
```json
{ "job_id": "uuid-del-job" }
```

### 3. Consultar el resultado

```bash
curl http://localhost:8000/api/v1/newsletters/{job_id}
```

Mientras procesa:
```json
{ "status": "pending" }
```

Cuando termina:
```json
{ "status": "done", "html": "<!DOCTYPE html>..." }
```

---

## Uso desde CLI (sin API)

```bash
# Sin perfil
poetry run python -m doctorate_reader.cli "política fiscal" --top-n 5 > newsletter.html

# Crear perfil interactivo
poetry run python -m doctorate_reader.cli --setup-profile ~/.doctorate_reader/profile.yaml

# Con perfil (ranking semántico)
poetry run python -m doctorate_reader.cli "política fiscal" \
  --profile ~/.doctorate_reader/profile.yaml > newsletter.html
```

---

## Endpoints completos

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/profiles` | Crear perfil |
| `GET` | `/api/v1/profiles/{id}` | Obtener perfil |
| `PUT` | `/api/v1/profiles/{id}` | Actualizar perfil |
| `DELETE` | `/api/v1/profiles/{id}` | Eliminar perfil |
| `POST` | `/api/v1/newsletters` | Lanzar generación (async) |
| `GET` | `/api/v1/newsletters/{job_id}` | Consultar resultado |
| `GET` | `/api/v1/health` | Health check |

Documentación interactiva completa: `http://localhost:8000/docs`

---

## Variables de entorno

| Variable | Por defecto | Descripción |
|----------|-------------|-------------|
| `LLM_MODEL` | `ollama/qwen2:7b` | Modelo litellm para resúmenes |
| `OLLAMA_HOST` | `http://localhost:11434` | URL del servidor Ollama |
| `DB_PATH` | `/data/doctorate_reader.db` | Ruta del fichero SQLite |
