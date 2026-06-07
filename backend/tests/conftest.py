"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from app.domain.entities.transcript import Transcript, TranscriptSegment
from app.domain.entities.video import VideoId
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.interfaces.transcript_provider import TranscriptProvider


class FakeTranscriptProvider(TranscriptProvider):
    def __init__(self, transcript: Transcript) -> None:
        self._transcript = transcript
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    async def fetch(self, video_id: VideoId, languages: tuple[str, ...]) -> Transcript:
        self.calls.append((str(video_id), languages))
        return self._transcript


class FakeLLMProvider(LLMProvider):
    def __init__(self, chunks: list[str]) -> None:
        self._chunks = chunks
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    async def stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        for chunk in self._chunks:
            yield chunk


@pytest.fixture
def sample_transcript() -> Transcript:
    return Transcript(
        video_id="dQw4w9WgXcQ",
        language="en",
        is_generated=False,
        segments=(
            TranscriptSegment(text="Hello", start=0.0, duration=1.0),
            TranscriptSegment(text="world", start=1.0, duration=1.0),
        ),
    )


@pytest.fixture
def fake_transcript_provider(sample_transcript: Transcript) -> FakeTranscriptProvider:
    return FakeTranscriptProvider(sample_transcript)


@pytest.fixture
def fake_llm_provider() -> FakeLLMProvider:
    return FakeLLMProvider(["Hello ", "summary"])
