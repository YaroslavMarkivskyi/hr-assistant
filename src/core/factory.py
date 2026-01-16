"""
Factory module for initializing and configuring FastAPI application components.
"""
import logging
from fastapi import FastAPI, APIRouter

from api.webhooks import router as webhooks_router
from api.system import router as system_router


logger = logging.getLogger(__name__)


def register_routers(app: FastAPI) -> None:
    """
    Register API routers with the FastAPI application.
    Args:
        app: FastAPI application instance
    """
    api_router = APIRouter(prefix="/api")
    
    api_router.include_router(system_router)
    api_router.include_router(webhooks_router)
    
    app.include_router(api_router)
    
    logger.info("API routers registered")


__all__ = (
    "register_routers",
)

