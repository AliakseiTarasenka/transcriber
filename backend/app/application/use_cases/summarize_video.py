"""Use case: stream a summary of a YouTube video."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.application.dto.summary_events import (
    SummaryDoneEvent,
    SummaryErrorEvent,
    SummaryEvent,
    SummaryMetaEvent,
    SummaryTextEvent,
)
from app.application.use_cases.get_transcript import GetTranscriptUseCase
from app.application.use_cases.prompts import build_system_prompt, build_user_prompt
from app.core.logging import get_logger
from app.domain.entities.summary import SummaryRequest
from app.domain.entities.transcript import Transcript
from app.domain.exceptions.errors import DomainError
from app.domain.interfaces.llm_provider import LLMProvider

logger = get_logger(__name__)


@dataclass(slots=True)
class SummarizeVideoUseCase:
    """Orchestrates: fetch transcript → stream LLM summary as events.

    The limits are injected at composition time (typically from
    :class:`Settings`), not hardcoded, so they can be tuned per environment.
    """

    get_transcript: GetTranscriptUseCase
    llm_provider: LLMProvider
    max_transcript_chars: int
    max_output_tokens: int

    async def execute(self, request: SummaryRequest) -> AsyncIterator[SummaryEvent]:
        # 1. Fetch transcript ---------------------------------------------------
        try:
            transcript = await self.get_transcript.execute(request.url, request.lang)
        except DomainError as exc:
            logger.warning("transcript_fetch_failed", error=str(exc))
            yield SummaryErrorEvent(text=str(exc))
            return
        except Exception as exc:
            logger.exception("transcript_fetch_unexpected_error")
            yield SummaryErrorEvent(text=f"Unexpected error: {exc}")
            return

        # 2. Build prompts & emit meta -----------------------------------------
        text = transcript.truncate(self.max_transcript_chars)
        yield self._build_meta_event(transcript, len(text))

        system_prompt = build_system_prompt(request.mode, request.lang)
        user_prompt = build_user_prompt(
            text,
            request.custom_prompt,
            transcript_language=transcript.language,
        )

        # 3. Stream LLM output --------------------------------------------------
        try:
            async for chunk in self.llm_provider.stream(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=self.max_output_tokens,
            ):
                if chunk:
                    yield SummaryTextEvent(text=chunk)
        except DomainError as exc:
            logger.warning("llm_failed", error=str(exc))
            yield SummaryErrorEvent(text=str(exc))
            return

        yield SummaryDoneEvent()

    def _build_meta_event(self, transcript: Transcript, sent_chars: int) -> SummaryMetaEvent:
        original = transcript.char_count
        truncated = sent_chars < original
        logger.info(
            "transcript_truncated" if truncated else "transcript_ready",
            original_chars=original,
            sent_chars=sent_chars,
            limit=self.max_transcript_chars,
            segments=len(transcript.segments),
            language=transcript.language,
            is_generated=transcript.is_generated,
        )
        return SummaryMetaEvent(
            chars=sent_chars,
            lang=transcript.language,
            original_chars=original,
            truncated=truncated,
            segments=len(transcript.segments),
        )
