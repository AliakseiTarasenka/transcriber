"""Domain-level exception hierarchy."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidVideoUrlError(DomainError):
    """Raised when a video URL/id cannot be parsed or is malformed."""


class TranscriptNotFoundError(DomainError):
    """Raised when no transcript is available for the video."""


class TranscriptProviderError(DomainError):
    """Raised when the transcript provider fails (network, blocked, etc.)."""


class LLMError(DomainError):
    """Raised when the LLM provider fails."""
