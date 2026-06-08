"""Anthropic Claude streaming adapter implementing :class:`LLMProvider`."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import httpx
from anthropic import APIError as AnthropicAPIError
from anthropic import AsyncAnthropic

from app.core.logging import get_logger
from app.domain.exceptions.errors import LLMError
from app.infrastructure.config.settings import Settings, get_settings

logger = get_logger(__name__)


@dataclass(slots=True)
class AnthropicLLMAdapter:
    """Concrete LLM provider using Anthropic's streaming Messages API."""

    settings: Settings = field(default_factory=get_settings)
    _client: AsyncAnthropic | None = field(default=None, init=False, repr=False)

    # ------------------------------------------------------------------
    # Convenience properties — delegate to settings so callers never need
    # to reach into self.settings directly.
    # ------------------------------------------------------------------

    @property
    def api_key(self) -> str:
        return self.settings.anthropic_api_key

    @property
    def model(self) -> str:
        return self.settings.anthropic_model

    @property
    def temperature(self) -> float:
        return self.settings.anthropic_temperature

    @property
    def max_output_tokens(self) -> int:
        return self.settings.max_output_tokens

    # ------------------------------------------------------------------
    # Client lifecycle
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,  # None → use settings.max_output_tokens
    ) -> AsyncIterator[str]:
        """Stream response tokens as they arrive from the Anthropic API."""
        client = self._get_client()
        effective_max_tokens = max_tokens if max_tokens is not None else self.max_output_tokens
        try:
            async with client.messages.stream(
                model=self.model,
                max_tokens=effective_max_tokens,
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
