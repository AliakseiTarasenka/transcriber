# 🎬 Transcriber

Web application to fetch a YouTube video transcript and generate an AI-powered
summary based on a custom prompt. Streams Claude's response live via SSE.

- **Backend**: FastAPI (Python 3.12+) — Clean Architecture
- **Frontend**: Next.js 15 (App Router) + React 19 + TypeScript
- **AI**: Anthropic Claude (streaming)
- **Transcripts**: `youtube-transcript-api`
- **Transport**: Server-Sent Events (SSE)

---

## Project layout

```
transcriber/
├── backend/                       # FastAPI app — Clean Architecture
│   ├── app/
│   │   ├── domain/                # Entities, interfaces, exceptions (pure)
│   │   ├── application/           # Use cases + DTOs
│   │   ├── infrastructure/        # YouTube + Anthropic adapters, settings
│   │   ├── api/                   # FastAPI routes, schemas, DI, SSE
│   │   ├── core/                  # Logging
│   │   └── main.py                # ASGI app factory
│   ├── tests/                     # unit + integration
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                      # Next.js app
│   ├── src/
│   │   ├── app/                   # Pages, layout, global styles
│   │   ├── components/            # SummarizeForm, SummaryView
│   │   ├── hooks/                 # useSummaryStream
│   │   ├── services/              # API client, SSE parser
│   │   ├── lib/                   # Config helpers
│   │   └── types/                 # Shared API types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml             # Run everything together
└── README.md
```

### Why Clean Architecture?

The dependency rule points inward only:

```
api  →  application  →  domain  ←  infrastructure
```

- **`domain`** has zero external dependencies — pure business rules
  (`VideoId`, `Transcript`, `SummaryRequest`, abstract `TranscriptProvider`
  and `LLMProvider` ports).
- **`application`** orchestrates use cases (`SummarizeVideoUseCase`,
  `GetTranscriptUseCase`) by depending only on domain abstractions.
- **`infrastructure`** provides concrete adapters
  (`YouTubeTranscriptApiAdapter`, `AnthropicLLMAdapter`) that implement
  domain ports — easy to swap for tests or alternative providers.
- **`api`** is the FastAPI delivery layer: thin routes, Pydantic schemas,
  DI wiring, SSE serialization.

Tests use fake providers (`FakeTranscriptProvider`, `FakeLLMProvider`) and
never touch the network.

---

## Quickstart

### 1. Local development (recommended for active dev)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
cp .env.example .env             # then fill ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

**Frontend** (in another terminal):

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000.

### 2. Docker Compose

```bash
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend  → http://localhost:8000 (Swagger at `/docs`)

---

## API

| Method | URL                                | Description                  |
|--------|------------------------------------|------------------------------|
| GET    | `/api/v1/health`                   | Liveness probe               |
| POST   | `/api/v1/summarize`                | Stream summary via SSE       |
| GET    | `/api/v1/transcript/{video_ref}`   | Raw transcript (JSON)        |

### `POST /api/v1/summarize`

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "mode": "summary",
  "lang": "ru",
  "prompt": "Focus on technical details"
}
```

- `mode` — `summary` | `bullets` | `detailed` | `qa`
- `lang` — `ru` | `en` | `auto`
- `prompt` — optional free-form user instruction

### SSE event types

| Event   | Payload                                         |
|---------|-------------------------------------------------|
| `meta`  | `{ "type": "meta",  "chars": 12345, "lang": "en" }` |
| `text`  | `{ "type": "text",  "text": "..." }`            |
| `done`  | `{ "type": "done" }`                            |
| `error` | `{ "type": "error", "text": "..." }`            |

---

## Testing

```bash
cd backend
pip install -e ".[dev]"
pytest --cov=app
```

The frontend uses `tsc --noEmit` (`npm run type-check`) and ESLint.

---

## Limitations

- Only videos with subtitles (manual or auto-generated) are supported.
- YouTube may rate-limit/block server IPs — consider configuring proxies or
  cookie auth in `youtube-transcript-api` if you hit this.
- Transcripts are truncated to 12,000 characters by default to control token
  cost (configurable via `MAX_TRANSCRIPT_CHARS`).

## License

See [LICENSE](LICENSE).
