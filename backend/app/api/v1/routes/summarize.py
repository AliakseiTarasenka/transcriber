"""POST /summarize — streams summary chunks as Server-Sent Events.

The route is intentionally thin: it converts the HTTP payload into a domain
:class:`SummaryRequest` and hands off to :class:`SummaryEventStreamer`, which
owns all SSE framing and disconnect handling.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.api.dependencies import SummarizeUseCaseDep, SummaryEventStreamerDep
from app.api.schemas.summarize import SummarizeRequest
from app.domain.entities.summary import SummaryRequest

router = APIRouter(tags=["summarize"])


@router.post(
    "/summarize",
    summary="Stream a summary of a YouTube video via SSE",
    response_class=EventSourceResponse,
)
async def summarize(
    payload: SummarizeRequest,
    request: Request,
    use_case: SummarizeUseCaseDep,
    streamer: SummaryEventStreamerDep,
) -> EventSourceResponse:
    domain_request = SummaryRequest(
        url=payload.url,
        mode=payload.mode,
        lang=payload.lang,
        custom_prompt=payload.prompt,
    )
    return streamer.stream(
        use_case=use_case,
        domain_request=domain_request,
        request=request,
    )
