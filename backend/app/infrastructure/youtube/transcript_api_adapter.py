"""Adapter over youtube-transcript-api implementing TranscriptProvider."""

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


@dataclass(slots=True)
class YouTubeTranscriptApiAdapter:
    """Transcript provider backed by blocking youtube-transcript-api."""

    executor: ThreadPoolExecutor
    timeout_seconds: float = 30.0

    async def fetch(self, video_id: VideoId, languages: tuple[str, ...]) -> Transcript:
        """Fetch transcript without blocking the event loop."""
        normalized_languages = languages or ("en",)

        loop = asyncio.get_running_loop()

        try:
            return await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self._fetch_sync,
                    video_id,
                    normalized_languages,
                ),
                timeout=self.timeout_seconds,
            )
        except TimeoutError as exc:
            logger.warning(
                "youtube_fetch_timeout",
                video_id=str(video_id),
                timeout_seconds=self.timeout_seconds,
            )
            raise TranscriptProviderError(
                f"Timed out while fetching transcript for video {video_id}"
            ) from exc
        except (TranscriptNotFoundError, TranscriptProviderError):
            raise
        except Exception as exc:
            logger.exception(
                "youtube_unexpected_error",
                video_id=str(video_id),
                languages=list(normalized_languages),
                error_type=type(exc).__name__,
            )
            raise TranscriptProviderError(f"Unexpected transcript error: {exc}") from exc

    @staticmethod
    def _fetch_sync(video_id: VideoId, languages: tuple[str, ...]) -> Transcript:
        vid = str(video_id)
        api = YouTubeTranscriptApi()

        try:
            fetched = api.fetch(vid, languages=list(languages))
        except Exception as exc:
            _raise_domain_error(exc, vid, languages)
            raise  # unreachable, keeps type checkers happy

        segments = tuple(
            TranscriptSegment(
                text=snippet.text,
                start=float(snippet.start),
                duration=float(snippet.duration),
            )
            for snippet in fetched.snippets
            if snippet.text
        )

        return Transcript(
            video_id=vid,
            language=getattr(fetched, "language_code", languages[0]),
            segments=segments,
            is_generated=bool(getattr(fetched, "is_generated", False)),
        )


def _raise_domain_error(
    exc: BaseException,
    video_id: str,
    languages: tuple[str, ...],
) -> None:
    """Map youtube-transcript-api errors to domain exceptions."""
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
                "YouTube blocked the request from this IP. Configure proxy or cookie auth."
            ) from exc

        case CouldNotRetrieveTranscript():
            raise TranscriptProviderError(f"Failed to retrieve transcript: {exc}") from exc

        case _:
            raise exc
