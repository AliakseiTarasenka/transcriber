# Settings Flow: .env → Use Case

This document shows how `MAX_TRANSCRIPT_CHARS` and `MAX_OUTPUT_TOKENS` flow from
configuration to the use case layer.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│ .env (or OS environment)                                            │
│                                                                     │
│   MAX_TRANSCRIPT_CHARS=200000                                       │
│   MAX_OUTPUT_TOKENS=8192                                            │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ infrastructure/config/settings.py                                   │
│                                                                     │
│   class Settings(BaseSettings):                                     │
│       max_transcript_chars: int = Field(default=200_000, ...)       │
│       max_output_tokens: int = Field(default=8_192, ...)            │
│                                                                     │
│   @lru_cache                                                        │
│   def get_settings() -> Settings:                                   │
│       return Settings()  # Pydantic reads from .env                 │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ api/dependencies/providers.py  (Composition Root)                   │
│                                                                     │
│   def _get_summarize_use_case(                                      │
│       get_transcript: GetTranscriptUseCaseDep,                      │
│       llm_provider: _LLMProviderDep,                                │
│       settings: _SettingsDep,  ◄─────────── injected by FastAPI    │
│   ) -> SummarizeVideoUseCase:                                       │
│       return SummarizeVideoUseCase(                                 │
│           get_transcript=get_transcript,                            │
│           llm_provider=llm_provider,                                │
│           max_transcript_chars=settings.max_transcript_chars, ◄──┐  │
│           max_output_tokens=settings.max_output_tokens,        ◄─┼─ injected here
│       )                                                            │  │
└───────────────────────┬────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ application/use_cases/summarize_video.py                            │
│                                                                     │
│   @dataclass(slots=True)                                            │
│   class SummarizeVideoUseCase:                                      │
│       get_transcript: GetTranscriptUseCase                          │
│       llm_provider: LLMProvider                                     │
│       max_transcript_chars: int  ◄────────────────────────────────┐ │
│       max_output_tokens: int     ◄──────────────────────────────┐ │ │
│                                                                  │ │ │
│       async def execute(self, request: SummaryRequest):          │ │ │
│           # ...                                                  │ │ │
│           text = transcript.truncate(self.max_transcript_chars) ─┘ │ │
│           # ...                                                    │ │
│           async for chunk in self.llm_provider.stream(             │ │
│               ...,                                                 │ │
│               max_tokens=self.max_output_tokens,  ─────────────────┘ │
│           ):                                                         │
│               yield SummaryTextEvent(text=chunk)                     │
└──────────────────────────────────────────────────────────────────────┘
```

## Key design decisions

### ✅ Why **no defaults** in the use case?

```python
# ❌ BAD — hardcoded in application layer, can't tune without editing code:
class SummarizeVideoUseCase:
    max_transcript_chars: int = 200_000
    max_output_tokens: int = 8_192
```

```python
# ✅ GOOD — injected at composition time, tunable via .env:
class SummarizeVideoUseCase:
    max_transcript_chars: int
    max_output_tokens: int
```

- **Testability**: Tests can pass tight limits (e.g. `max_transcript_chars=100`)
  without mocking or monkey-patching.
- **Flexibility**: Dev/staging/prod can have different limits via `.env` alone.
- **SRP**: The use case doesn't know "what's a good default" — that's a
  deployment concern, owned by `Settings`.

### ✅ Why **not import `Settings`** into the use case?

```python
# ❌ BAD — violates Clean Architecture (app layer imports infrastructure):
from app.infrastructure.config.settings import get_settings

class SummarizeVideoUseCase:
    def __init__(self, ...):
        settings = get_settings()
        self.max_transcript_chars = settings.max_transcript_chars
```

```python
# ✅ GOOD — use case is pure; DI wires it at the composition root:
@dataclass(slots=True)
class SummarizeVideoUseCase:
    max_transcript_chars: int  # injected by providers.py
```

- **Dependency rule**: `application/` must not know about `infrastructure/`.
- **Isolation**: The use case is a plain dataclass — trivially unit-testable,
  zero coupling to FastAPI or Pydantic.

### ✅ Why `@dataclass(slots=True)`?

- **Memory efficiency**: `slots=True` saves ~40 bytes per instance by skipping
  `__dict__`.
- **Safety**: Typos like `uc.max_transcrpit_chars` fail at attribute-access time
  instead of silently creating a new field.

---

## How to change limits

### At runtime (via `.env`)
```bash
# backend/.env
MAX_TRANSCRIPT_CHARS=500000  # for very long videos
MAX_OUTPUT_TOKENS=16384      # for detailed long-form summaries
```

Restart `uvicorn` — changes take effect immediately.

### Per-environment
```bash
# backend/.env.development
MAX_TRANSCRIPT_CHARS=100000
MAX_OUTPUT_TOKENS=2048

# backend/.env.production
MAX_TRANSCRIPT_CHARS=400000
MAX_OUTPUT_TOKENS=16384
```

Load the appropriate file via `ENV_FILE=.env.production uvicorn ...`.

### Via environment variables (Docker, Kubernetes)
```yaml
# docker-compose.yml
environment:
  MAX_TRANSCRIPT_CHARS: 300000
  MAX_OUTPUT_TOKENS: 12288
```

---

## Verification

Run this to confirm values flow correctly:
```bash
cd backend
MAX_TRANSCRIPT_CHARS=50000 MAX_OUTPUT_TOKENS=2048 \
  python -c "
from app.infrastructure.config.settings import get_settings
from app.api.dependencies.providers import _get_summarize_use_case, ...

get_settings.cache_clear()
s = get_settings()
uc = _get_summarize_use_case(..., settings=s)
assert uc.max_transcript_chars == 50_000
assert uc.max_output_tokens == 2_048
print('✓ Settings flow correctly')
"
```
