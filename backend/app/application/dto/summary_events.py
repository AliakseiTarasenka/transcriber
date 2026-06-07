"""Streaming summary events emitted by the use case to the presentation layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union


@dataclass(frozen=True, slots=True)
class SummaryMetaEvent:
    type: Literal["meta"] = "meta"
    chars: int = 0  # chars actually sent to the LLM (after any truncation)
    lang: str = ""
    original_chars: int = 0  # full transcript length before truncation
    truncated: bool = False  # whether the transcript was truncated
    segments: int = 0  # number of subtitle segments in the source


@dataclass(frozen=True, slots=True)
class SummaryTextEvent:
    text: str
    type: Literal["text"] = "text"


@dataclass(frozen=True, slots=True)
class SummaryDoneEvent:
    type: Literal["done"] = "done"


@dataclass(frozen=True, slots=True)
class SummaryErrorEvent:
    text: str
    type: Literal["error"] = "error"


SummaryEvent = Union[
    SummaryMetaEvent,
    SummaryTextEvent,
    SummaryDoneEvent,
    SummaryErrorEvent,
]
