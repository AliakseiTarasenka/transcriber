"""Video-related value objects."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.exceptions.errors import InvalidVideoUrlError

# Matches YouTube IDs in common URL forms: watch?v=, youtu.be/, /embed/, /shorts/.
_YOUTUBE_ID_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([0-9A-Za-z_-]{11})"),
    re.compile(r"^([0-9A-Za-z_-]{11})$"),
)


@dataclass(frozen=True, slots=True)
class VideoId:
    """Immutable, validated YouTube video identifier."""

    value: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[0-9A-Za-z_-]{11}", self.value):
            raise InvalidVideoUrlError(f"Invalid YouTube video id: {self.value!r}")

    @classmethod
    def from_url(cls, url: str) -> VideoId:
        """Extract a :class:`VideoId` from a YouTube URL or bare id."""
        if not url or not isinstance(url, str):
            raise InvalidVideoUrlError("URL must be a non-empty string")

        url = url.strip()
        for pattern in _YOUTUBE_ID_PATTERNS:
            match = pattern.search(url)
            if match:
                return cls(match.group(1))

        raise InvalidVideoUrlError(f"Cannot extract video id from URL: {url!r}")

    def __str__(self) -> str:
        return self.value
