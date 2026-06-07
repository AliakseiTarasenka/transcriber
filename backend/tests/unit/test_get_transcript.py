"""Tests for the GetTranscriptUseCase language fall-back logic."""

from __future__ import annotations

import pytest

from app.application.use_cases.get_transcript import GetTranscriptUseCase
from tests.conftest import FakeTranscriptProvider


@pytest.mark.asyncio
async def test_requested_language_first_then_fallbacks(
    fake_transcript_provider: FakeTranscriptProvider,
) -> None:
    use_case = GetTranscriptUseCase(
        transcript_provider=fake_transcript_provider,
        default_lang="ru",
    )

    await use_case.execute("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "ru")

    _, languages = fake_transcript_provider.calls[-1]
    # Requested ("ru") first, then fallbacks (en, pl) — deduplicated.
    assert languages == ("ru", "en", "pl")


@pytest.mark.asyncio
async def test_polish_request_includes_polish_first(
    fake_transcript_provider: FakeTranscriptProvider,
) -> None:
    use_case = GetTranscriptUseCase(
        transcript_provider=fake_transcript_provider,
        default_lang="ru",
    )

    await use_case.execute("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "pl")

    _, languages = fake_transcript_provider.calls[-1]
    assert languages[0] == "pl"
    assert "en" in languages
    assert "ru" in languages


@pytest.mark.asyncio
async def test_auto_uses_full_fallback_set(
    fake_transcript_provider: FakeTranscriptProvider,
) -> None:
    use_case = GetTranscriptUseCase(
        transcript_provider=fake_transcript_provider,
        default_lang="ru",
    )

    await use_case.execute("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "auto")

    _, languages = fake_transcript_provider.calls[-1]
    assert languages == ("en", "ru", "pl")


@pytest.mark.asyncio
async def test_unknown_language_still_attempted_first(
    fake_transcript_provider: FakeTranscriptProvider,
) -> None:
    """A user-provided lang we don't know about should still be tried first."""
    use_case = GetTranscriptUseCase(
        transcript_provider=fake_transcript_provider,
        default_lang="ru",
    )

    await use_case.execute("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "de")

    _, languages = fake_transcript_provider.calls[-1]
    assert languages == ("de", "en", "ru", "pl")


def test_language_priority_is_deduplicated() -> None:
    """If the requested language is already in the fallback set, no duplicates."""
    result = GetTranscriptUseCase._language_priority("en")
    assert result == ("en", "ru", "pl")
    assert len(result) == len(set(result))
