"""Schemas for the /transcript endpoint."""

from __future__ import annotations

from pydantic import BaseModel

from app.domain.entities.transcript import Transcript


class TranscriptSegmentSchema(BaseModel):
    text: str
    start: float
    duration: float


class TranscriptResponse(BaseModel):
    video_id: str
    language: str
    is_generated: bool
    char_count: int
    segments: list[TranscriptSegmentSchema]

    @classmethod
    def from_domain(cls, transcript: Transcript) -> TranscriptResponse:
        return cls(
            video_id=transcript.video_id,
            language=transcript.language,
            is_generated=transcript.is_generated,
            char_count=transcript.char_count,
            segments=[
                TranscriptSegmentSchema(
                    text=segment.text,
                    start=segment.start,
                    duration=segment.duration,
                )
                for segment in transcript.segments
            ],
        )
