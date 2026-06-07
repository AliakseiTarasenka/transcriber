"""Summary domain entities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SummaryMode(StrEnum):
    """Available summary modes."""

    SUMMARY = "summary"
    BULLETS = "bullets"
    DETAILED = "detailed"
    QA = "qa"


@dataclass(frozen=True, slots=True)
class SummaryRequest:
    """Input for the summarize use case."""

    url: str
    mode: SummaryMode = SummaryMode.SUMMARY
    lang: str = "ru"
    custom_prompt: str | None = None
