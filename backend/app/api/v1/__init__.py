"""API v1 package."""

from fastapi import APIRouter

from app.api.v1.routes import health, summarize, transcript

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(summarize.router)
api_router.include_router(transcript.router)

__all__ = ["api_router"]
