"""Tests for the SSE encoder layer.

These tests are pure — no FastAPI, no I/O — which is exactly the point of
extracting the encoder into its own module.
"""

from __future__ import annotations

import json

from app.api.sse import EventEncoder, SSEMessage, SummaryEventEncoder
from app.application.dto.summary_events import (
    SummaryDoneEvent,
    SummaryErrorEvent,
    SummaryMetaEvent,
    SummaryTextEvent,
)


def test_encoder_satisfies_protocol() -> None:
    encoder: EventEncoder[SummaryMetaEvent] = SummaryEventEncoder()
    assert hasattr(encoder, "encode")


def test_encodes_meta_event() -> None:
    encoder = SummaryEventEncoder()
    message = encoder.encode(SummaryMetaEvent(chars=100, lang="ru", original_chars=200, segments=5))

    assert isinstance(message, SSEMessage)
    assert message.event == "meta"
    payload = json.loads(message.data)
    assert payload == {
        "type": "meta",
        "chars": 100,
        "lang": "ru",
        "original_chars": 200,
        "truncated": False,
        "segments": 5,
    }


def test_encodes_text_event_preserves_unicode() -> None:
    encoder = SummaryEventEncoder()
    message = encoder.encode(SummaryTextEvent(text="Привіт"))

    # ensure_ascii=False keeps Cyrillic readable on the wire.
    assert "Привіт" in message.data
    assert message.event == "text"


def test_encodes_done_and_error_events() -> None:
    encoder = SummaryEventEncoder()
    assert encoder.encode(SummaryDoneEvent()).event == "done"

    err = encoder.encode(SummaryErrorEvent(text="boom"))
    assert err.event == "error"
    assert json.loads(err.data)["text"] == "boom"


def test_to_mapping_matches_sse_starlette_contract() -> None:
    msg = SSEMessage(event="text", data='{"x":1}')
    assert msg.to_mapping() == {"event": "text", "data": '{"x":1}'}
