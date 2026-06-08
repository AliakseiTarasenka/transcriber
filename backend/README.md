# Transcriber Backend

FastAPI backend for YouTube transcript fetching & AI summarization built with **Clean Architecture**.

## Features

- 🎥 **YouTube transcript extraction** — supports multiple languages with fallback
- 🤖 **AI summarization** — streaming responses from Claude 4.x (Anthropic)
- 🌍 **Multi-language support** — English, Russian, Polish, + auto-translation
- 📡 **SSE streaming** — real-time token-by-token output
- 🏗 **Clean Architecture** — domain/application/infrastructure separation
- 🔒 **Type-safe** — mypy strict mode, 100% typed
- ✅ **Production-ready** — pre-commit hooks, linting, CI/CD

## Architecture

```
app/
├── domain/             # Pure business rules (no external deps)
│   ├── entities/       # Core entities (Transcript, SummaryRequest, VideoId)
│   ├── interfaces/     # Abstract ports (TranscriptProvider, LLMProvider)
│   └── exceptions/     # Domain-specific exceptions
├── application/        # Use cases orchestrating domain logic
│   ├── use_cases/      # SummarizeVideo, GetTranscript
│   ├── dto/            # SSE event DTOs
│   └── prompts/        # LLM prompt builders
├── infrastructure/     # Concrete adapters to external systems
│   ├── youtube/        # youtube-transcript-api v1.x adapter
│   ├── llm/            # Anthropic Claude async streaming adapter
│   └── config/         # Settings (pydantic-settings, .env)
├── api/                # FastAPI presentation layer
│   ├── v1/routes/      # HTTP endpoints (health, summarize, transcript)
│   ├── schemas/        # Pydantic request/response models
│   ├── dependencies/   # DI container (composition root)
│   └── sse/            # Server-Sent Events encoder + streamer
├── core/               # Cross-cutting concerns (structlog JSON logging)
└── main.py             # ASGI app factory with lifespan management
```

**Key Design Decisions:**
- **Dependency Rule:** `api → application → domain ← infrastructure` (domain has zero imports)
- **Dependency Injection:** All adapters wired at the composition root (`api/dependencies/providers.py`)
- **Protocol-based:** Domain defines `LLMProvider` / `TranscriptProvider` protocols; infrastructure implements them
- **Testable:** Use cases accept injected dependencies → trivial to mock

## Quickstart

### Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies + dev tools
pip install -e ".[dev]"

# 3. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY=sk-ant-...

# 4. Install pre-commit hooks (optional but recommended)
pre-commit install

# 5. Run the server
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for interactive API documentation.

### Docker

```bash
# From project root:
docker compose up --build
```

Backend runs on port 8000, frontend on 3000.

## API Reference

| Method | Path                       | Description                  |
|--------|----------------------------|------------------------------|
| GET    | `/health`                  | Health check                 |
| POST   | `/api/v1/summarize`        | Stream summary via SSE       |
| GET    | `/api/v1/transcript/{id}`  | Fetch raw transcript JSON    |

### POST /api/v1/summarize

**Request body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "mode": "summary",  // "summary" | "bullets" | "detailed" | "qa"
  "lang": "en",       // "ru" | "en" | "pl" | "auto"
  "prompt": "Focus on key takeaways"  // optional custom instructions
}
```

**Response:** Server-Sent Events stream

```
event: meta
data: {"type":"meta","chars":12345,"lang":"en","original_chars":12345,"truncated":false,"segments":42}

event: text
data: {"type":"text","text":"The video discusses..."}

event: text
data: {"type":"text","text":" key concepts..."}

event: done
data: {"type":"done"}
```

### GET /api/v1/transcript/{video_ref}

Fetch raw transcript (no summarization).

**Parameters:**
- `video_ref` — YouTube URL or 11-char video ID
- `lang` (query, optional) — Preferred language code

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "segments": [
    {"text": "Hello world", "start": 0.0, "duration": 2.5}
  ],
  "is_generated": true
}
```

## Configuration

All settings are loaded from environment variables or `.env` file. See [docs/CONFIGURATION.md](./docs/CONFIGURATION.md) for full reference.

**Key settings:**

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-5-20250929` | Claude model ID |
| `ANTHROPIC_TEMPERATURE` | `0.3` | Sampling temperature (0.0–1.0) |
| `MAX_TRANSCRIPT_CHARS` | `200_000` | Max chars sent to LLM |
| `MAX_OUTPUT_TOKENS` | `8_192` | Max tokens in LLM response |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins |

**Example `.env`:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_TEMPERATURE=0.3
MAX_TRANSCRIPT_CHARS=200000
MAX_OUTPUT_TOKENS=8192
```

## Development

### Code Quality & Linting

This project uses **black**, **isort**, **flake8**, **ruff**, and **mypy** with **pre-commit hooks** for automated code quality.

```bash
# Run all linters
make lint

# Auto-fix formatting
make format

# Run tests with coverage
make test

# Full CI check (lint + test)
make check

# Install pre-commit hooks (runs on every commit)
pre-commit install
```

See [README_LINTING.md](./README_LINTING.md) for quick reference or [docs/LINTING.md](./docs/LINTING.md) for full guide.

**All commands:**
```bash
make help         # Show all available commands
make install      # Install deps + pre-commit hooks
make lint         # ruff + flake8 + mypy
make format       # black + isort + ruff --fix
make test         # pytest with coverage
make test-fast    # pytest without coverage
make pre-commit   # run pre-commit on all files
make clean        # remove build/cache artifacts
make check        # lint + test (CI-ready)
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Watch mode (requires pytest-watch)
ptw

# Run specific test
pytest tests/unit/test_summarize_use_case.py -v
```

**Test structure:**
```
tests/
├── unit/              # Unit tests (no I/O, fakes for ports)
│   ├── test_get_transcript.py
│   ├── test_summarize_use_case.py
│   ├── test_video_id.py
│   ├── test_prompts.py
│   └── test_sse_encoder.py
├── integration/       # Integration tests (real adapters, optional)
└── conftest.py        # Shared fixtures (FakeTranscriptProvider, FakeLLMProvider)
```

Current coverage: **48%** (unit tests for domain + application layers). See [LINTING_SETUP_COMPLETE.md](./LINTING_SETUP_COMPLETE.md) for coverage goals.

## Documentation

| Document | Description |
|---|---|
| [README_LINTING.md](./README_LINTING.md) | Linting quick reference |
| [docs/LINTING.md](./docs/LINTING.md) | Comprehensive linting guide |
| [docs/CONFIGURATION.md](./docs/CONFIGURATION.md) | All environment variables |
| [docs/SETTINGS_FLOW.md](./docs/SETTINGS_FLOW.md) | How settings propagate (architecture) |
| [docs/COST_OPTIMIZATION.md](./docs/COST_OPTIMIZATION.md) | 🔥 Reduce API costs by 90%+ |
| [docs/PERFORMANCE_OPTIMIZATION.md](./docs/PERFORMANCE_OPTIMIZATION.md) | ⚡ Scale to 1000+ concurrent users |
| [docs/OPTIMIZATION_QUICKSTART.md](./docs/OPTIMIZATION_QUICKSTART.md) | Quick wins for cost & performance |
| [LINTING_SETUP_COMPLETE.md](./LINTING_SETUP_COMPLETE.md) | Linting setup summary |

## Tech Stack

| Category | Technology |
|---|---|
| **Framework** | FastAPI 0.115+ |
| **ASGI Server** | Uvicorn with uvloop |
| **LLM** | Anthropic Claude 4.x (async streaming) |
| **Transcript** | youtube-transcript-api 1.x |
| **Validation** | Pydantic v2 |
| **Logging** | structlog (JSON) |
| **Streaming** | sse-starlette (SSE) |
| **Testing** | pytest + pytest-asyncio + pytest-cov |
| **Linting** | ruff + flake8 + mypy (strict) |
| **Formatting** | black + isort |
| **Hooks** | pre-commit |

## Project Structure Highlights

### Clean Architecture Layers

**Domain Layer** (`app/domain/`)
- Zero external dependencies (pure Python)
- Defines entities (`Transcript`, `SummaryRequest`, `VideoId`)
- Defines abstract ports (`LLMProvider`, `TranscriptProvider`)
- Domain exceptions (`TranscriptNotFoundError`, `LLMError`)

**Application Layer** (`app/application/`)
- Orchestrates domain logic
- Use cases: `GetTranscriptUseCase`, `SummarizeVideoUseCase`
- Depends on domain ports (injected at runtime)
- Returns domain events (`SummaryMetaEvent`, `SummaryTextEvent`, etc.)

**Infrastructure Layer** (`app/infrastructure/`)
- Implements domain ports
- `YouTubeTranscriptApiAdapter` → `TranscriptProvider`
- `AnthropicLLMAdapter` → `LLMProvider`
- `Settings` (pydantic-settings for .env)

**API Layer** (`app/api/`)
- FastAPI routes
- Pydantic schemas (HTTP contracts)
- Dependency injection wiring (`dependencies/providers.py`)
- SSE encoder + streamer

### Dependency Injection Flow

```
Settings (.env)
   ↓
get_settings() — cached singleton
   ↓
Dependency factories (providers.py)
   ↓  ↓  ↓
   ↓  ↓  AnthropicLLMAdapter (singleton per config)
   ↓  YouTubeTranscriptApiAdapter (singleton)
   ↓
   GetTranscriptUseCase (per request)
   ↓
   SummarizeVideoUseCase (per request)
   ↓
   SummaryEventStreamer (singleton)
   ↓
FastAPI route handlers (injected via Depends(...))
```

All composition happens in **one file** (`api/dependencies/providers.py`) — the only place concrete adapters are named.

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

**On every push/PR:**
1. **Lint job** — ruff, flake8, black --check, isort --check, mypy
2. **Test job** — pytest with coverage → Codecov

Both must pass for merge.

**Local CI check:**
```bash
make check  # Runs lint + test (same as CI)
```

## Deployment

### Environment Variables (Production)

Set these in your deployment environment:

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_TEMPERATURE=0.3
MAX_TRANSCRIPT_CHARS=200000
MAX_OUTPUT_TOKENS=8192
APP_ENV=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

### Docker

```bash
docker build -t transcriber-backend .
docker run -p 8000:8000 --env-file .env transcriber-backend
```

Or use docker-compose from project root:
```bash
docker compose up --build
```

### Scaling

- The app is **stateless** — scale horizontally with a load balancer
- `AnthropicLLMAdapter` reuses an httpx connection pool (singleton per config)
- `YouTubeTranscriptApiAdapter` is stateless (singleton)
- No database — all data is ephemeral (transcripts fetched on-demand)

## Troubleshooting

### "No transcript found"

**Cause:** Video has no subtitles, or the requested language is unavailable.

**Solution:** The app tries fallback languages (`en`, `ru`, `pl`). If none work, the video has no captions. Try `lang=auto` to accept any language — the LLM will translate during summarization.

### "YouTube blocked the request"

**Cause:** YouTube rate-limits or blocks server IPs.

**Solution:** Configure a proxy or cookie-based auth (see `youtube-transcript-api` docs). Or run the app from a residential IP.

### "Transcript was truncated"

**Cause:** Video is longer than `MAX_TRANSCRIPT_CHARS`.

**Solution:** Increase the limit in `.env`:
```bash
MAX_TRANSCRIPT_CHARS=500000
```

See [docs/CONFIGURATION.md](./docs/CONFIGURATION.md) for limits vs. cost trade-offs.

### "Output cut off mid-sentence"

**Cause:** Hit `MAX_OUTPUT_TOKENS`.

**Solution:** Increase in `.env`:
```bash
MAX_OUTPUT_TOKENS=16384
```

### "Tests fail with missing imports"

**Cause:** Dev dependencies not installed.

**Solution:**
```bash
pip install -e ".[dev]"
```

### "Pre-commit is slow on first run"

**Cause:** Installing hook environments (3-5 minutes first time).

**Solution:** Subsequent runs are ~1-2 seconds. To skip: `git commit --no-verify`.

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Run linters: `make lint` (or let pre-commit do it)
5. Run tests: `make test`
6. Commit: `git commit -m "feat: add my feature"`
7. Push: `git push origin feature/my-feature`
8. Open a PR

**Pre-commit hooks run automatically** on every commit. To bypass (for WIP commits):
```bash
git commit --no-verify -m "WIP: work in progress"
```

## License

MIT (or specify your license)

## Credits

- [FastAPI](https://fastapi.tiangolo.com/) — modern Python web framework
- [Anthropic Claude](https://www.anthropic.com/) — LLM provider
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) — transcript extraction
- Clean Architecture principles by Robert C. Martin

---

**Need help?** See [docs/](./docs/) for detailed guides or open an issue.
