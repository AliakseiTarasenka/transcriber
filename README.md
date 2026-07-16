# Transcriber

Web application for fetching a YouTube transcript and streaming an AI-generated
summary from Anthropic Claude. The app is split into a FastAPI backend and a
Next.js frontend.

- **Backend**: FastAPI, Python 3.12+, Clean Architecture
- **Frontend**: Next.js 15 App Router, React 19, TypeScript
- **AI**: Anthropic Claude streaming responses
- **Transcripts**: `youtube-transcript-api`
- **Transport**: Server-Sent Events (SSE)

## Current Functionality

- Fetch transcripts by YouTube URL or 11-character video ID.
- Generate summaries in `summary`, `bullets`, `detailed`, or `qa` mode.
- Choose output language from Russian, English, Polish, or automatic detection
  in the frontend. The backend accepts `auto` or any two-letter language code.
- Add an optional custom prompt of up to 2,000 characters.
- Stream summary text live with smooth client-side batching.
- Cancel an in-progress summary request.
- Show transcript metadata: output language, source segment count, characters
  sent to the LLM, original transcript length, and truncation status.
- Copy the generated context summary from the output panel with the copy icon.
- Fetch raw transcript JSON from the API without summarization.

## Project Layout

```text
transcriber/
├── backend/
│   ├── app/
│   │   ├── domain/                # Entities, ports, domain exceptions
│   │   ├── application/           # Use cases, DTOs, prompt builders
│   │   ├── infrastructure/        # YouTube, Anthropic, settings adapters
│   │   ├── api/                   # FastAPI routes, schemas, DI, SSE
│   │   ├── core/                  # Logging
│   │   └── main.py                # ASGI app
│   ├── tests/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── Makefile
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                   # App Router pages, layout, global styles
│   │   ├── components/            # Form, summary output, chat UI components
│   │   ├── hooks/                 # Streaming state hooks
│   │   ├── lib/                   # Config and YouTube helpers
│   │   ├── services/              # API client and SSE parser
│   │   └── types/                 # Shared API types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Architecture

The backend follows Clean Architecture:

```text
api -> application -> domain <- infrastructure
```

- `domain` contains pure business entities and protocols.
- `application` orchestrates use cases such as summarizing a video and fetching
  a transcript.
- `infrastructure` implements external adapters for YouTube transcripts,
  Anthropic streaming, and settings.
- `api` handles FastAPI routes, schemas, dependency injection, and SSE framing.

Tests can inject fake transcript and LLM providers without network access.

## Quickstart

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY
make up
```

Backend:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

The frontend defaults to `http://localhost:8000` for the backend. To override
it, create `frontend/.env.local`:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Docker Compose

```bash
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## API

| Method | URL                              | Description            |
| ------ | -------------------------------- | ---------------------- |
| GET    | `/api/v1/health`                 | Liveness probe         |
| POST   | `/api/v1/summarize`              | Stream summary via SSE |
| GET    | `/api/v1/transcript/{video_ref}` | Raw transcript JSON    |

### `POST /api/v1/summarize`

Request body:

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "mode": "summary",
  "lang": "en",
  "prompt": "Focus on technical details"
}
```

Fields:

- `url`: YouTube URL or 11-character video ID.
- `mode`: `summary`, `bullets`, `detailed`, or `qa`.
- `lang`: `auto` or a two-letter language code. The frontend offers `ru`,
  `en`, `pl`, and `auto`.
- `prompt`: optional custom instruction, max 2,000 characters.

SSE events:

```text
event: meta
data: {"type":"meta","chars":12345,"lang":"en","original_chars":14000,"truncated":true,"segments":82}

event: text
data: {"type":"text","text":"The video discusses..."}

event: done
data: {"type":"done"}
```

Event types:

| Event   | Payload                                                                 |
| ------- | ----------------------------------------------------------------------- |
| `meta`  | LLM input chars, language, original chars, truncation flag, segment count |
| `text`  | Next streamed summary chunk                                             |
| `done`  | Stream completed                                                        |
| `error` | Stream failed                                                           |

### `GET /api/v1/transcript/{video_ref}`

Fetches the raw transcript without summarization.

Query parameters:

- `lang`: optional preferred language code.

Response:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "is_generated": true,
  "char_count": 12345,
  "segments": [
    { "text": "Hello world", "start": 0.0, "duration": 2.5 }
  ]
}
```

## Configuration

Backend settings are loaded from `backend/.env`.

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `ANTHROPIC_API_KEY` | required | Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-5-20250929` | Claude model ID |
| `ANTHROPIC_TEMPERATURE` | `0.0` | Sampling temperature |
| `MAX_TRANSCRIPT_CHARS` | `200000` | Max transcript chars sent to the LLM |
| `MAX_OUTPUT_TOKENS` | `8192` | Max tokens in the Claude response |
| `DEFAULT_LANG` | `ru` | Default output language |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed browser origins |
| `YOUTUBE_FETCH_WORKERS` | `10` | YouTube transcript fetch worker count |
| `YOUTUBE_FETCH_TIMEOUT_SECONDS` | `30` | YouTube transcript fetch timeout |

Frontend setting:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `NEXT_PUBLIC_BACKEND_URL` | `http://localhost:8000` | Browser-visible backend base URL |

## Development

Backend commands:

```bash
cd backend
make help        # show available commands
make install     # install dev dependencies and pre-commit hooks
make lint        # ruff, flake8, mypy
make format      # isort, black, ruff --fix
make test        # pytest with coverage
make test-fast   # pytest without coverage
make check       # lint + test
make up          # run uvicorn on port 8000
```

Frontend commands:

```bash
cd frontend
npm run dev
npm run lint
npm run type-check
npm run build
```

At the moment, `npm run type-check` is blocked unless the frontend's `uuid`
dependency is added or the unused chat hook is adjusted. The active summary
page and linting do not depend on that package.

## Limitations

- Only videos with manual or auto-generated subtitles are supported.
- YouTube may rate-limit or block server IPs.
- Long transcripts are truncated according to `MAX_TRANSCRIPT_CHARS`; the UI
  shows when truncation happened.

## License

See [LICENSE](LICENSE).
