"""Port for fetching video transcripts."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.entities.transcript import Transcript
from app.domain.entities.video import VideoId


@runtime_checkable
class TranscriptProvider(Protocol):
    """Abstraction over a transcript-fetching service."""

    async def fetch(self, video_id: VideoId, languages: tuple[str, ...]) -> Transcript:
        """Fetch a transcript, preferring the given language order."""
        ...
