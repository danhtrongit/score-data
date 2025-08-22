"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import zscore, fscore

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(zscore.router)
api_router.include_router(fscore.router)
