"""Main API v1 router aggregating all sub-routers."""

from fastapi import APIRouter

from backend.api.v1.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router, tags=["health"])
