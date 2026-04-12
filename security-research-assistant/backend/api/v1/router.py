"""Main API v1 router aggregating all sub-routers."""

from fastapi import APIRouter

from backend.api.v1.architecture import router as architecture_router
from backend.api.v1.profile import router as profile_router
from backend.api.v1.reports import router as reports_router
from backend.api.v1.conversations import router as conversations_router
from backend.api.v1.documents import router as documents_router
from backend.api.v1.health import router as health_router
from backend.api.v1.query import router as query_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router, tags=["health"])
api_v1_router.include_router(documents_router)
api_v1_router.include_router(query_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(architecture_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(profile_router)
