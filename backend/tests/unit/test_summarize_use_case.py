"""Tests for the SummarizeVideoUseCase."""

from __future__ import annotations

import pytest

from app.application.dto.summary_events import (
    SummaryDoneEvent,
    SummaryLoadingEvent,
    SummaryMetaEvent,
    SummaryTextEvent,
)
from app.application.use_cases.get_transcript import GetTranscriptUseCase
from app.application.use_cases.summarize_video import SummarizeVideoUseCase
from app.domain.entities.summary import SummaryMode, SummaryRequest
from tests.conftest import FakeLLMProvider, FakeTranscriptProvider


@pytest.mark.asyncio
async def test_summarize_emits_meta_text_done(
    fake_transcript_provider: FakeTranscriptProvider,
    fake_llm_provider: FakeLLMProvider,
) -> None:
    use_case = SummarizeVideoUseCase(
        get_transcript=GetTranscriptUseCase(
            transcript_provider=fake_transcript_provider,
            default_lang="en",
        ),
        llm_provider=fake_llm_provider,
        max_transcript_chars=100,
        max_output_tokens=1024,
    )

    events = [
        event
        async for event in use_case.execute(
            SummaryRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                mode=SummaryMode.SUMMARY,
                lang="en",
                custom_prompt="focus on greetings",
            )
        )
    ]

    # First event should be loading
    assert isinstance(events[0], SummaryLoadingEvent)
    assert "Fetching" in events[0].message

    # Second event should be meta
    assert isinstance(events[1], SummaryMetaEvent)
    assert events[1].lang == "en"
    assert events[1].chars > 0

    # Text events
    text_events = [e for e in events if isinstance(e, SummaryTextEvent)]
    assert [e.text for e in text_events] == ["Hello ", "summary"]

    # Last event should be done
    assert isinstance(events[-1], SummaryDoneEvent)

    # Verify custom prompt was passed
    assert "focus on greetings" in (fake_llm_provider.last_user_prompt or "")
