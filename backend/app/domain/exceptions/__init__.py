"""Domain exceptions."""

from app.domain.exceptions.errors import (
    DomainError,
    InvalidVideoUrlError,
    LLMError,
    TranscriptNotFoundError,
    TranscriptProviderError,
)

__all__ = [
    "DomainError",
    "InvalidVideoUrlError",
    "LLMError",
    "TranscriptNotFoundError",
    "TranscriptProviderError",
]
