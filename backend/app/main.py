"""ASGI app factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies.providers import get_llm_provider
from app.api.v1 import api_router
from app.core.logging import configure_logging, get_logger
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.anthropic_adapter import AnthropicLLMAdapter

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Manage app startup and shutdown (yielding to FastAPI for the runtime)."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    logger.info(
        "app_starting",
        app_name=settings.app_name,
        env=settings.app_env,
        model=settings.anthropic_model,
    )
    yield
    # Release LLM client connection pool, if it was created during the run.
    llm = get_llm_provider(settings)
    if isinstance(llm, AnthropicLLMAdapter):
        await llm.aclose()
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
