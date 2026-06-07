"""FastAPI dependency providers — the Composition Root.

This module is the **only** place where concrete infrastructure adapters
(:class:`AnthropicLLMAdapter`, :class:`YouTubeTranscriptApiAdapter`) are
instantiated. All other layers depend exclusively on the abstract ports
(``LLMProvider``, ``TranscriptProvider``) defined in ``app.domain.interfaces``.

Swapping a provider therefore requires changing exactly one factory below.

Public surface (what other modules should import):

* :data:`GetTranscriptUseCaseDep`   — for ``GET /transcript`` route handlers.
* :data:`SummarizeUseCaseDep`       — for ``POST /summarize`` route handlers.
* :data:`SummaryEventStreamerDep`   — SSE streamer used by the summarize route.
* :func:`get_llm_provider`          — used by the app lifespan to ``aclose()``
  the shared httpx connection pool on shutdown.

Everything else is an implementation detail.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.api.sse import SummaryEventEncoder, SummaryEventStreamer
from app.application.use_cases.get_transcript import GetTranscriptUseCase
from app.application.use_cases.summarize_video import SummarizeVideoUseCase
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.interfaces.transcript_provider import TranscriptProvider
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.llm.anthropic_adapter import AnthropicLLMAdapter
from app.infrastructure.youtube.transcript_api_adapter import YouTubeTranscriptApiAdapter

# --- Internal type aliases (private) ----------------------------------------

_SettingsDep = Annotated[Settings, Depends(get_settings)]


# --- Provider factories (singletons where appropriate) -----------------------


@lru_cache(maxsize=1)
def _get_transcript_provider() -> TranscriptProvider:
    """Singleton transcript provider (stateless, safe to share)."""
    return YouTubeTranscriptApiAdapter()


@lru_cache(maxsize=1)
def _build_llm_provider(api_key: str, model: str, temperature: float) -> LLMProvider:
    """Cache the LLM adapter per config tuple to reuse its httpx connection pool."""
    return AnthropicLLMAdapter(api_key=api_key, model=model, temperature=temperature)


def get_llm_provider(settings: _SettingsDep) -> LLMProvider:
    """LLM provider bound to current settings.

    Public because the app lifespan calls it directly (with a manually-built
    ``Settings``) to release the underlying httpx pool on shutdown.
    """
    return _build_llm_provider(
        api_key=settings.anthropic_api_key,
        model=settings.anthropic_model,
        temperature=settings.anthropic_temperature,
    )


# --- Use-case factories (private — exposed only via the *Dep aliases) -------

_TranscriptProviderDep = Annotated[TranscriptProvider, Depends(_get_transcript_provider)]
_LLMProviderDep = Annotated[LLMProvider, Depends(get_llm_provider)]


def _get_get_transcript_use_case(
    transcript_provider: _TranscriptProviderDep,
    settings: _SettingsDep,
) -> GetTranscriptUseCase:
    return GetTranscriptUseCase(
        transcript_provider=transcript_provider,
        default_lang=settings.default_lang,
    )


GetTranscriptUseCaseDep = Annotated[GetTranscriptUseCase, Depends(_get_get_transcript_use_case)]


def _get_summarize_use_case(
    get_transcript: GetTranscriptUseCaseDep,
    llm_provider: _LLMProviderDep,
    settings: _SettingsDep,
) -> SummarizeVideoUseCase:
    return SummarizeVideoUseCase(
        get_transcript=get_transcript,
        llm_provider=llm_provider,
        max_transcript_chars=settings.max_transcript_chars,
        max_output_tokens=settings.max_output_tokens,
    )


SummarizeUseCaseDep = Annotated[SummarizeVideoUseCase, Depends(_get_summarize_use_case)]


# --- Transport-layer factories ----------------------------------------------


@lru_cache(maxsize=1)
def _get_summary_event_streamer() -> SummaryEventStreamer:
    """Singleton SSE streamer; encoder is stateless so safe to share."""
    return SummaryEventStreamer(encoder=SummaryEventEncoder())


SummaryEventStreamerDep = Annotated[SummaryEventStreamer, Depends(_get_summary_event_streamer)]
