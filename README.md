# Freddy AI Assistant

An AI-powered assistant that summarises articles and PDFs with the personality
and voice of myself (Frederick Obeng-Nyarko). Built with FastAPI, OpenAI GPT-5.2, and React/Next.js.
Deployed on Fly.io.

---

## Features

- Summarise any article by pasting a URL
- Summarise uploaded PDF documents
- Streams responses in real time via Server-Sent Events (SSE)
- Persistent conversation threads
- My personality baked into every response
- Structured JSON logging with correlation IDs
- Graceful error handling at every layer

---

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| API          | FastAPI 0.133+                    |
| LLM          | OpenAI GPT-5.2 (pluggable)        |
| Database     | PostgreSQL + SQLAlchemy + Alembic |
| Deployment   | Fly.io (Docker)                   |
| PDF Parsing  | PyMuPDF                           |
| URL Scraping | httpx + BeautifulSoup4            |

---

## Project Structure
```
app/
├── core/           # DI container, exceptions, logging, events
├── api/            # FastAPI routes and dependencies
├── llm/            # LLM providers (Strategy pattern)
├── tools/          # URL scraper and PDF reader (Strategy pattern)
├── agents/         # Agent logic and orchestration
├── memory/         # Short-term conversation memory
├── services/       # Business logic layer
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response schemas
└── db/             # Database session and Alembic migrations
```

---

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL running locally
- [uv](https://docs.astral.sh/uv/) package manager
- An OpenAI API key

### 1. Clone the repository
```bash
git clone https://github.com/Fred-O-Nyarko/personal-ai-agent
cd personal-ai-agent
```

### 2. Create and activate virtual environment
```bash
uv venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
uv sync
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Open `.env` and fill in your values:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxx
DATABASE_URL=postgresql+asyncpg://localhost/freddyai
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-5.2
LOG_LEVEL=INFO
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### 5. Create the database
```bash
psql postgres -c "CREATE DATABASE freddyai;"
```

### 6. Run migrations
```bash
alembic upgrade head
```

### 7. Start the server
```bash
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`.
Interactive docs are at `http://localhost:8000/docs`.

---

## API Reference

### Health Check
```
GET /healthz
```
```json
{ "status": "ok" }
```

---

### Run Agent — Summarise a URL
```
POST /api/v1/agents/run
Content-Type: multipart/form-data
```

| Field       | Type   | Required | Description                  |
|-------------|--------|----------|------------------------------|
| `url`       | string | yes*     | Article URL to summarise     |
| `file`      | file   | yes*     | PDF file to summarise        |
| `thread_id` | string | no       | Thread to attach the run to  |

*Either `url` or `file` is required, not both.

Returns a `text/event-stream` SSE response:
```
data: {"type": "token",  "content": "Systems thinking is..."}
data: {"type": "token",  "content": " a discipline for..."}
data: {"type": "done",   "run_id": "abc-123"}
data: {"type": "error",  "code": "TOOL_ERROR", "message": "..."}
```

**Example — URL:**
```bash
curl -X POST http://localhost:8000/api/v1/agents/run \
  -F "url=https://example.com/article" | cat
```

**Example — PDF:**
```bash
curl -X POST http://localhost:8000/api/v1/agents/run \
  -F "file=@/path/to/document.pdf" | cat
```

---

### Threads
```
GET    /api/v1/threads              # list all threads
POST   /api/v1/threads              # create a thread
GET    /api/v1/threads/{id}         # get a thread
DELETE /api/v1/threads/{id}         # delete a thread
```

**Create a thread:**
```bash
curl -X POST http://localhost:8000/api/v1/threads \
  -H "Content-Type: application/json" \
  -d '{"title": "AI Research"}' | python -m json.tool
```

---

### Tools
```
GET /api/v1/tools
```

Returns all registered tools:
```json
{
  "tools": [
    { "name": "url_scraper", "description": "Fetch and extract article text from a URL." },
    { "name": "pdf_reader",  "description": "Extract text content from an uploaded PDF file." }
  ]
}
```

---

## Swapping the LLM Provider

The LLM layer uses the Strategy pattern — swapping providers requires
no changes to agent or service code.

### Add Anthropic

1. Create `app/llm/providers/anthropic_provider.py` extending `LLMProvider`
2. Register it in `app/llm/factory.py`:
```python
from app.llm.providers.anthropic_provider import AnthropicProvider
LLMProviderFactory.register("anthropic", AnthropicProvider)
```

3. Update `.env`:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

No other changes required.

---

## Adding a New Tool

1. Create `app/tools/my_tool.py` extending `BaseTool`
2. Register it in `app/core/container.py`:
```python
from app.tools.my_tool import MyTool
registry.register(MyTool())
```

3. Call it from any agent via the registry:
```python
result = await self._registry.execute("my_tool", MyToolInput(...))
```

---

## Deployment — Fly.io

### Prerequisites
```bash
brew install flyctl
fly auth login
```

### First deploy
```bash
fly launch --name personal-ai-assistant --region lhr --no-deploy
fly secrets set OPENAI_API_KEY=sk-proj-xxxxxxxx
fly secrets set DATABASE_URL=postgresql+asyncpg://...
fly deploy
```

### Subsequent deploys
```bash
fly deploy
```

### View logs
```bash
fly logs
```

### Open in browser
```bash
fly open
```

---

## Environment Variables

| Variable               | Required | Default   | Description                          |
|------------------------|----------|-----------|--------------------------------------|
| `OPENAI_API_KEY`       | yes      | —         | OpenAI secret key                    |
| `DATABASE_URL`         | yes      | —         | PostgreSQL async connection string   |
| `LLM_PROVIDER`         | no       | `openai`  | LLM provider key                     |
| `OPENAI_MODEL`         | no       | `gpt-5.2` | Model identifier                     |
| `ALLOWED_ORIGINS`      | no       | localhost | Comma-separated CORS origins         |
| `MAX_CONTENT_TOKENS`   | no       | `12000`   | Max tokens extracted from content    |
| `REQUEST_TIMEOUT_SECONDS` | no    | `15`      | HTTP timeout for URL scraping        |
| `LOG_LEVEL`            | no       | `INFO`    | Logging verbosity                    |
| `DEBUG`                | no       | `false`   | Enables SQLAlchemy query logging     |

---

## Error Handling

All errors return structured JSON:
```json
{
  "error": "TOOL_ERROR",
  "message": "HTTP 403 fetching: https://example.com"
}
```

| Code               | Status | Cause                              |
|--------------------|--------|------------------------------------|
| `TOOL_ERROR`       | 422    | URL fetch or PDF parse failure     |
| `TOOL_NOT_FOUND`   | 404    | Unknown tool requested             |
| `LLM_ERROR`        | 502    | OpenAI API failure or rate limit   |
| `THREAD_NOT_FOUND` | 404    | Thread ID does not exist           |
| `UNKNOWN_PROVIDER` | 500    | LLM_PROVIDER env var is invalid    |
| `INTERNAL_ERROR`   | 500    | Unhandled exception                |

Errors during streaming are delivered as SSE error events so the
client always receives a clean response regardless of where the
failure occurred.

---

## Logs

All logs are structured JSON written to stdout — compatible with
Fly.io log drain and external aggregators like Logtail or Papertrail.

Every log entry includes a `correlation_id` for full request tracing:
```json
{
  "asctime": "2026-02-25 07:46:54,500",
  "levelname": "INFO",
  "name": "app.core.log",
  "message": "run_started",
  "correlation_id": "fa25d619-df49-493c-855d-22992a5c77f8",
  "run_id": "2e2a1638-9fcf-42ac-ba6f-a2e890a5623f",
  "tool": "url_scraper"
}
```

---

## License

MIT