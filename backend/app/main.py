"""ASGI app factory."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies.providers import get_llm_provider
from app.api.v1 import api_router
from app.core.logging import configure_logging, get_logger
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.anthropic_adapter import AnthropicLLMAdapter
from app.infrastructure.youtube.transcript_api_adapter import YouTubeTranscriptApiAdapter

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown resources."""
    settings = get_settings()
    configure_logging(settings.log_level)

    logger = get_logger(__name__)

    youtube_executor = ThreadPoolExecutor(
        max_workers=settings.youtube_fetch_workers,
        thread_name_prefix="youtube_fetch_",
    )

    app.state.youtube_executor = youtube_executor
    app.state.transcript_provider = YouTubeTranscriptApiAdapter(
        executor=youtube_executor,
        timeout_seconds=settings.youtube_fetch_timeout_seconds,
    )

    logger.info(
        "app_starting",
        app_name=settings.app_name,
        env=settings.app_env,
        model=settings.anthropic_model,
        youtube_fetch_workers=settings.youtube_fetch_workers,
        youtube_fetch_timeout_seconds=settings.youtube_fetch_timeout_seconds,
    )

    try:
        yield
    finally:
        llm = get_llm_provider(settings)

        if isinstance(llm, AnthropicLLMAdapter):
            await llm.aclose()

        youtube_executor.shutdown(wait=True, cancel_futures=True)

        logger.info("app_stopping")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Transcriber API",
        description="YouTube transcript fetcher & AI summarizer (Clean Architecture).",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()
