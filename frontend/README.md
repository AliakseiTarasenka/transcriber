# Transcriber Frontend

Next.js 15 (App Router) + React 19 + TypeScript frontend for the Transcriber service.

## Architecture

```
src/
├── app/                 # Next.js App Router (pages, layout, global styles)
├── components/          # Reusable presentational components
├── hooks/               # React hooks (e.g. useSummaryStream)
├── services/            # API client (fetch wrappers, SSE parser)
├── lib/                 # Cross-cutting helpers (config)
└── types/               # Shared TypeScript types mirroring backend schemas
```

The frontend is intentionally thin: it owns presentation and streaming UX,
while all business logic lives in the FastAPI backend (Clean Architecture).

## Quickstart

```bash
cd frontend
cp .env.example .env.local   # adjust BACKEND_URL if needed
npm install
npm run dev                  # http://localhost:3000
```

The backend must be running on `http://localhost:8000` (or set
`NEXT_PUBLIC_BACKEND_URL` accordingly).

## Streaming

We post to `POST /api/v1/summarize` with `Accept: text/event-stream` and parse
SSE frames manually (`EventSource` is GET-only and cannot send a JSON body).
See `src/services/transcriberApi.ts` and `src/hooks/useSummaryStream.ts`.
