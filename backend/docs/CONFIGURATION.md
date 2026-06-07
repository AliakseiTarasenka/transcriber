# Configuration Guide

## Environment Variables

All settings are loaded from `backend/.env` (or environment variables in production).
Copy `backend/.env.example` to `backend/.env` and customize as needed.

### Core Settings

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key (`sk-ant-...`) |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-5-20250929` | Claude model ID — see [available models](#claude-models) |
| `ANTHROPIC_TEMPERATURE` | `0.3` | Sampling temperature: `0.0` = deterministic, `1.0` = creative |

### Limits

| Variable | Default | Range | Description |
|---|---|---|---|
| `MAX_TRANSCRIPT_CHARS` | `200_000` | `1_000` – `600_000` | Max characters sent to Claude from the transcript |
| `MAX_OUTPUT_TOKENS` | `8_192` | `128` – `64_000` | Max tokens in Claude's response |
| `DEFAULT_LANG` | `ru` | ISO 639-1 code | Default language when user picks "auto" |

#### How limits work

1. **`MAX_TRANSCRIPT_CHARS`** — transcripts longer than this are truncated at
   the nearest sentence/word boundary. The full transcript is always fetched
   from YouTube; this limit only controls what's sent to Claude.

   - **Default (200k)** fits ~3-hour videos.
   - **For 5+ hour videos:** increase to `400_000` or `500_000`.
   - **Hard cap:** Claude 4.x supports ~600k chars input, but leave room for
     prompts + completion.

2. **`MAX_OUTPUT_TOKENS`** — Claude stops generating after this many tokens.
   1 token ≈ 0.75 words.

   - **Default (8192)** ≈ 6000 words — sufficient for detailed summaries.
   - **For very long outputs:** increase to `16_384` or `32_768` (Opus 4.5 caps
     at 32k; Sonnet/Haiku 4.5 at 64k).

#### Cost implications

Anthropic charges per token. Example for Sonnet 4.5 (as of 2026):
- Input: ~$3 / 1M tokens
- Output: ~$15 / 1M tokens

A 200k-char transcript (~70k input tokens) + 8k output tokens costs:
- Input: $0.21
- Output: $0.12
- **Total: ~$0.33 per summary**

### Server

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | HTTP port |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

### Logging

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `APP_ENV` | `development` | Environment tag (appears in logs) |

---

## Claude Models

Available on your account (verified 2026-06-06):

| Model ID | Display Name | Use Case |
|---|---|---|
| `claude-haiku-4-5-20251001` | Claude Haiku 4.5 | Fast, cheap (~1/10 the cost of Sonnet) |
| `claude-sonnet-4-5-20250929` | Claude Sonnet 4.5 | **Default** — best balance |
| `claude-sonnet-4-6` | Claude Sonnet 4.6 | Newer Sonnet |
| `claude-opus-4-5-20251101` | Claude Opus 4.5 | Highest quality, slowest, priciest |
| `claude-opus-4-6` | Claude Opus 4.6 | |
| `claude-opus-4-7` | Claude Opus 4.7 | |
| `claude-opus-4-8` | Claude Opus 4.8 | Latest Opus |

To switch models, set in `.env`:
```bash
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
```

---

## Examples

### Cheap & fast (for development)
```bash
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_TEMPERATURE=0.3
MAX_TRANSCRIPT_CHARS=100000
MAX_OUTPUT_TOKENS=4096
```

### Production (balanced)
```bash
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_TEMPERATURE=0.3
MAX_TRANSCRIPT_CHARS=200000
MAX_OUTPUT_TOKENS=8192
```

### High-quality, long-form summaries
```bash
ANTHROPIC_MODEL=claude-opus-4-8
ANTHROPIC_TEMPERATURE=0.2
MAX_TRANSCRIPT_CHARS=400000
MAX_OUTPUT_TOKENS=16384
```

### Fully deterministic (for regression tests / evals)
```bash
ANTHROPIC_TEMPERATURE=0.0
```
