"""Tests for VideoId parsing."""

from __future__ import annotations

import pytest

from app.domain.entities.video import VideoId
from app.domain.exceptions.errors import InvalidVideoUrlError


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ"),
    ],
)
def test_from_url_extracts_id(url: str, expected: str) -> None:
    assert VideoId.from_url(url).value == expected


@pytest.mark.parametrize("url", ["", "not a url", "https://example.com/"])
def test_from_url_rejects_invalid(url: str) -> None:
    with pytest.raises(InvalidVideoUrlError):
        VideoId.from_url(url)
