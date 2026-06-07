"""Encoders for Server-Sent Events.

This module owns the **wire format** for SSE: how a domain event becomes a
single SSE frame ("event: ...\\ndata: ...\\n\\n"). It does **not** know about
HTTP, generators, or FastAPI — only about pure data transformation, so it is
trivially unit-testable.

The :class:`EventEncoder` Protocol decouples the route layer from any specific
event family (SRP + DIP): swapping :class:`SummaryEventEncoder` for, e.g., a
``ChatEventEncoder`` is a one-line change at the composition root.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Generic, Protocol, TypeVar

from app.application.dto.summary_events import SummaryEvent

E_contra = TypeVar("E_contra", contravariant=True)


@dataclass(frozen=True, slots=True)
class SSEMessage:
    """A single Server-Sent Events frame.

    The shape matches what ``sse-starlette``'s ``EventSourceResponse`` expects
    when yielded from a generator (``{"event": ..., "data": ...}``), so this
    object can be yielded as-is — but having it as a typed value object lets
    us swap the transport (e.g. WebSocket, plain JSON-lines) without touching
    business code.
    """

    event: str
    data: str

    def to_mapping(self) -> dict[str, str]:
        """Return the dict form expected by ``sse-starlette``."""
        return {"event": self.event, "data": self.data}


class EventEncoder(Protocol, Generic[E_contra]):
    """Encode a domain event into a transport-ready :class:`SSEMessage`.

    Generic over the event type so static type checkers catch mismatches at
    composition time (e.g. wiring a ``SummaryEventEncoder`` to a chat stream).
    """

    def encode(self, event: E_contra) -> SSEMessage: ...


class SummaryEventEncoder:
    """JSON-encodes :class:`SummaryEvent` instances into :class:`SSEMessage`.

    Stateless and pure — safe to reuse across requests (a single instance is
    typically registered as a FastAPI dependency).
    """

    __slots__ = ()

    def encode(self, event: SummaryEvent) -> SSEMessage:
        return SSEMessage(
            event=event.type,
            data=_dumps(asdict(event)),
        )


def _dumps(payload: dict[str, Any]) -> str:
    """Compact, UTF-8-friendly JSON serialization for SSE payloads."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
