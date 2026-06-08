"""Adapter over ``youtube-transcript-api`` (v1.x) implementing :class:`TranscriptProvider`."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    IpBlocked,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
)

from app.core.logging import get_logger
from app.domain.entities.transcript import Transcript, TranscriptSegment
from app.domain.entities.video import VideoId
from app.domain.exceptions.errors import TranscriptNotFoundError, TranscriptProviderError

logger = get_logger(__name__)

# Shared thread pool for YouTube fetches. Limits concurrent thread usage to
# prevent thread exhaustion under high load. The default thread pool (used by
# asyncio.to_thread) is unbounded, which can cause issues with many concurrent
# requests.
_EXECUTOR = ThreadPoolExecutor(
    max_workers=10,  # max concurrent YouTube fetches
    thread_name_prefix="youtube_fetch_",
)


@dataclass(slots=True)
class YouTubeTranscriptApiAdapter:
    """Concrete transcript provider backed by ``youtube-transcript-api`` >= 1.0."""

    async def fetch(self, video_id: VideoId, languages: tuple[str, ...]) -> Transcript:
        """Fetch a transcript off the event loop (the underlying lib is sync).

        Uses a bounded thread pool executor to prevent thread exhaustion under
        high concurrent load.
        """
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                _EXECUTOR,
                self._fetch_sync,
                video_id,
                languages,
            )
        except (TranscriptNotFoundError, TranscriptProviderError):
            raise
        except Exception as exc:
            logger.exception("youtube_unexpected_error", video_id=str(video_id))
            raise TranscriptProviderError(f"Unexpected transcript error: {exc}") from exc

    @staticmethod
    def _fetch_sync(video_id: VideoId, languages: tuple[str, ...]) -> Transcript:
        vid = str(video_id)
        api = YouTubeTranscriptApi()

        try:
            fetched = api.fetch(vid, languages=list(languages))
        except Exception as exc:
            _raise_domain_error(exc, vid, languages)

        segments = tuple(
            TranscriptSegment(
                text=snippet.text,
                start=float(snippet.start),
                duration=float(snippet.duration),
            )
            for snippet in fetched.snippets
        )

        return Transcript(
            video_id=vid,
            language=getattr(fetched, "language_code", languages[0] if languages else "en"),
            segments=segments,
            is_generated=bool(getattr(fetched, "is_generated", False)),
        )


def _raise_domain_error(exc: BaseException, video_id: str, languages: tuple[str, ...]) -> None:
    """Map ``youtube-transcript-api`` errors to our domain exceptions."""
    match exc:
        case TranscriptsDisabled():
            raise TranscriptNotFoundError(f"Transcripts are disabled for video {video_id}") from exc
        case NoTranscriptFound():
            raise TranscriptNotFoundError(
                f"No transcript found for video {video_id} in languages {list(languages)}"
            ) from exc
        case VideoUnavailable():
            raise TranscriptNotFoundError(f"Video {video_id} is unavailable") from exc
        case IpBlocked() | RequestBlocked():
            raise TranscriptProviderError(
                "YouTube blocked the request from this IP. Configure a proxy or cookie auth."
            ) from exc
        case CouldNotRetrieveTranscript():
            raise TranscriptProviderError(f"Failed to retrieve transcript: {exc}") from exc
        case _:
            raise exc
