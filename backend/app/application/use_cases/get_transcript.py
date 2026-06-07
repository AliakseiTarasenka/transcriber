"""Use case: fetch a raw transcript by video id/URL."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.logging import get_logger
from app.domain.entities.transcript import Transcript
from app.domain.entities.video import VideoId
from app.domain.interfaces.transcript_provider import TranscriptProvider

logger = get_logger(__name__)

# Curated set of broadly available languages we fall back to when the requested
# language has no transcript on YouTube. Order matters: English first because
# it's by far the most common, followed by other languages we explicitly
# support in the UI. Translation to the user's chosen output language is
# performed by the LLM downstream, so any of these is acceptable.
_FALLBACK_LANGUAGES: tuple[str, ...] = ("en", "ru", "pl")


@dataclass(slots=True)
class GetTranscriptUseCase:
    """Return the raw transcript for a given video id or URL.

    The use case is *language-tolerant*: it tries the user's preferred language
    first and then falls back to other widely-available languages. The actual
    translation to the requested output language happens later, in the LLM
    summarization step. This works well in practice because:

    1. YouTube's auto-translate is unavailable for many videos
       (``is_translatable=False``).
    2. Modern LLMs (Claude 3+) translate accurately while summarizing in a
       single pass — no separate translation step needed.
    """

    transcript_provider: TranscriptProvider
    default_lang: str = "ru"

    async def execute(self, video_ref: str, lang: str | None = None) -> Transcript:
        video_id = VideoId.from_url(video_ref)
        languages = self._language_priority(lang or self.default_lang)
        logger.info("fetching_transcript", video_id=str(video_id), languages=languages)
        return await self.transcript_provider.fetch(video_id, languages)

    @staticmethod
    def _language_priority(lang: str) -> tuple[str, ...]:
        """Build the language fall-back order passed to the transcript provider.

        ``"auto"`` means "any language is fine" — return the full fallback set.
        Otherwise, request the user's language first, then any remaining
        fallbacks (deduplicated, original order preserved).
        """
        if lang == "auto":
            return _FALLBACK_LANGUAGES
        # dict.fromkeys preserves insertion order while removing duplicates.
        return tuple(dict.fromkeys((lang, *_FALLBACK_LANGUAGES)))
