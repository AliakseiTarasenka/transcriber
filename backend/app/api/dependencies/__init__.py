"""Dependency-injection wiring for FastAPI routes.

Only the symbols actually consumed outside this package are re-exported.
Everything else in :mod:`providers` is an implementation detail.
"""

from app.api.dependencies.providers import (
    GetTranscriptUseCaseDep,
    SummarizeUseCaseDep,
    SummaryEventStreamerDep,
    get_llm_provider,
)

__all__ = [
    "GetTranscriptUseCaseDep",
    "SummarizeUseCaseDep",
    "SummaryEventStreamerDep",
    "get_llm_provider",
]
