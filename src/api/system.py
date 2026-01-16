from fastapi import APIRouter
from core.config import settings

from schemas.api import (
    APIHealthCheckResponse,
    APISystemInfoResponse
    )


router = APIRouter(
    prefix="/system",
    tags=["system"]
)


@router.get(
    "/health",
    response_model=APIHealthCheckResponse,
    description="Health check endpoint",
    status_code=200
    )
async def health():
    """Health check endpoint"""
    return APIHealthCheckResponse(status="ok")
    
@router.get(
    "/info",
    response_model=APISystemInfoResponse,
    description="Service info endpoint",
    status_code=200
    )
async def info():
    """Service info endpoint"""
    return APISystemInfoResponse(
        service=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION
    )


__all__ = (
    "router",
)

