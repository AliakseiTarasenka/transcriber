"""Domain abstractions (ports)."""

from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.interfaces.transcript_provider import TranscriptProvider

__all__ = ["LLMProvider", "TranscriptProvider"]
