"""GET /transcript/{video_id} — return the raw transcript."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies.providers import GetTranscriptUseCaseDep
from app.api.schemas.transcript import TranscriptResponse
from app.domain.exceptions.errors import (
    InvalidVideoUrlError,
    TranscriptNotFoundError,
    TranscriptProviderError,
)

router = APIRouter(tags=["transcript"])


@router.get(
    "/transcript/{video_ref:path}",
    response_model=TranscriptResponse,
    summary="Return the raw transcript for a YouTube video",
)
async def get_transcript(
    video_ref: str,
    use_case: GetTranscriptUseCaseDep,
    lang: str | None = Query(default=None, description="Preferred language code"),
) -> TranscriptResponse:
    try:
        transcript = await use_case.execute(video_ref, lang)
    except InvalidVideoUrlError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TranscriptNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TranscriptProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return TranscriptResponse.from_domain(transcript)
