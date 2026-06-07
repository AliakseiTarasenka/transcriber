"""Schemas for the /summarize endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.entities.summary import SummaryMode


class SummarizeRequest(BaseModel):
    """Body of POST /summarize."""

    url: str = Field(
        ...,
        description="YouTube video URL or 11-character video id",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )
    mode: SummaryMode = Field(
        default=SummaryMode.SUMMARY,
        description="Summary mode: summary | bullets | detailed | qa",
    )
    lang: str = Field(
        default="ru",
        description="Output language: ru | en | auto",
        pattern=r"^[a-zA-Z]{2}$|^auto$",
    )
    prompt: str | None = Field(
        default=None,
        description="Optional custom user prompt to refine the summary",
        max_length=2_000,
    )
