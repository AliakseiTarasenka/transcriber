"""Port for streaming LLM completions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Abstraction over a streaming LLM service."""

    def stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Stream model output as text chunks (async generator)."""
        ...
