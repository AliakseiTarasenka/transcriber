"""High-level SSE streaming for the summarize endpoint.

This module bridges the **application layer** (a use case yielding domain
events) and the **transport layer** (SSE frames over HTTP). Routes import a
single class — :class:`SummaryEventStreamer` — and call ``stream()``, which
returns a ready-to-use ``EventSourceResponse``.

Why a class instead of a free function?

* **SRP** — encoding (``EventEncoder``) and orchestration (this class) are
  separate, each independently replaceable / testable.
* **DIP** — the streamer depends on the abstract :class:`EventEncoder`
  Protocol, not on a concrete encoder.
* **Testability** — ``stream_events`` is an ``async`` generator with no FastAPI
  imports, so unit tests can drive it without spinning up a server.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass

from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from app.api.sse.encoder import EventEncoder
from app.application.dto.summary_events import SummaryEvent
from app.application.use_cases.summarize_video import SummarizeVideoUseCase
from app.core.logging import get_logger
from app.domain.entities.summary import SummaryRequest

logger = get_logger(__name__)

# Headers that disable buffering at every layer (browser, nginx, CDN) so chunks
# reach the client immediately. Kept here because they are part of the SSE
# transport contract — moving them to the route would couple it to SSE again.
_NO_BUFFER_HEADERS: Mapping[str, str] = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}

# Heartbeat interval (seconds) — keeps reverse proxies from idling the stream.
_PING_INTERVAL_SECONDS = 15


@dataclass(slots=True, frozen=True)
class SummaryEventStreamer:
    """Streams summary events from a use case to the client over SSE."""

    encoder: EventEncoder[SummaryEvent]

    def stream(
        self,
        *,
        use_case: SummarizeVideoUseCase,
        domain_request: SummaryRequest,
        request: Request,
    ) -> EventSourceResponse:
        """Build an ``EventSourceResponse`` that streams the use case output."""
        return EventSourceResponse(
            self._stream_events(use_case, domain_request, request),
            headers=dict(_NO_BUFFER_HEADERS),
            ping=_PING_INTERVAL_SECONDS,
            media_type="text/event-stream",
        )

    async def _stream_events(
        self,
        use_case: SummarizeVideoUseCase,
        domain_request: SummaryRequest,
        request: Request,
    ) -> AsyncIterator[dict[str, str]]:
        """Run the use case and yield encoded SSE frames until done or aborted."""
        async for event in use_case.execute(domain_request):
            if await request.is_disconnected():
                logger.info("sse_client_disconnected")
                break
            yield self.encoder.encode(event).to_mapping()
