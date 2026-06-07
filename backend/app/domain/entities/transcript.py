"""Transcript domain entities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import cached_property

# Sentence terminators, including CJK punctuation.
_SENTENCE_TERMINATORS: tuple[str, ...] = (". ", "! ", "? ", "。", "！", "？")
# Reject sentence-boundary cuts that lose more than this fraction of the window.
_MIN_SENTENCE_RATIO = 0.6
# Reject word-boundary cuts that lose more than this fraction of the window.
_MIN_WORD_RATIO = 0.8


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    """A single subtitle segment from a video."""

    text: str
    start: float
    duration: float


# NOTE: ``cached_property`` requires ``__dict__`` so we cannot use ``slots=True``.
@dataclass(frozen=True)
class Transcript:
    """Aggregate of transcript segments for a video."""

    video_id: str
    language: str
    segments: tuple[TranscriptSegment, ...] = field(default_factory=tuple)
    is_generated: bool = False

    @classmethod
    def from_segments(
        cls,
        video_id: str,
        language: str,
        segments: Iterable[TranscriptSegment],
        *,
        is_generated: bool = False,
    ) -> Transcript:
        return cls(
            video_id=video_id,
            language=language,
            segments=tuple(segments),
            is_generated=is_generated,
        )

    @cached_property
    def full_text(self) -> str:
        """Concatenate all segment texts with single spaces (computed once)."""
        return " ".join(s.text.strip() for s in self.segments if s.text)

    @property
    def char_count(self) -> int:
        return len(self.full_text)

    def truncate(self, max_chars: int) -> str:
        """Return transcript text truncated to at most ``max_chars`` characters.

        Prefers a sentence boundary, then a word boundary, to avoid cutting
        mid-word/mid-sentence which can confuse the LLM.
        """
        text = self.full_text
        if max_chars <= 0 or len(text) <= max_chars:
            return text

        head = text[:max_chars]

        # 1) Try sentence boundary close to the end of the window.
        for terminator in _SENTENCE_TERMINATORS:
            idx = head.rfind(terminator)
            if idx >= max_chars * _MIN_SENTENCE_RATIO:
                return head[: idx + 1].rstrip()

        # 2) Fall back to the last whitespace.
        idx = head.rfind(" ")
        if idx >= max_chars * _MIN_WORD_RATIO:
            return head[:idx].rstrip()

        # 3) Hard cut.
        return head
