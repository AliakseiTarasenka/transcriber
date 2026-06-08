"""Anthropic Claude streaming adapter implementing :class:`LLMProvider`."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import httpx
from anthropic import APIError as AnthropicAPIError
from anthropic import AsyncAnthropic

from app.core.logging import get_logger
from app.domain.exceptions.errors import LLMError

logger = get_logger(__name__)


@dataclass(slots=True)
class AnthropicLLMAdapter:
    """Concrete LLM provider using Anthropic's streaming Messages API.

    Sampling temperature controls output randomness:
      * ``0.0``  - fully deterministic, best for extractive / factual tasks.
      * ``0.3``  - default here: faithful summaries with light natural phrasing.
      * ``0.7+`` - creative writing / brainstorming.
      * ``1.0``  - Anthropic's API default (too high for summarization).
    """

    api_key: str
    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.3

    # Lazily-created shared client. Reusing a single ``AsyncAnthropic`` keeps
    # the underlying httpx connection pool warm across requests, reducing TTFB.
    _client: AsyncAnthropic | None = field(default=None, init=False, repr=False)

    def _get_client(self) -> AsyncAnthropic:
        if not self.api_key:
            raise LLMError("ANTHROPIC_API_KEY is not configured")
        if self._client is None:
            # Custom httpx client with tuned connection pool limits for better
            # throughput under concurrent load.
            http_client = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_connections=100,  # total concurrent connections
                    max_keepalive_connections=20,  # persistent connections
                ),
                timeout=httpx.Timeout(
                    60.0,  # total request timeout
                    connect=5.0,  # connection timeout
                ),
            )
            self._client = AsyncAnthropic(
                api_key=self.api_key,
                http_client=http_client,
            )
        return self._client

    async def stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        client = self._get_client()
        try:
            async with client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except AnthropicAPIError as exc:
            logger.warning("anthropic_api_error", error=str(exc))
            raise LLMError(f"Anthropic API error: {exc}") from exc

    async def aclose(self) -> None:
        """Release the shared httpx client (called from app shutdown)."""
        if self._client is not None:
            await self._client.close()
            self._client = None
