"""
Bootstrap module for initializing application dependencies and state.
"""
import logging
from fastapi import FastAPI
from core.config import Config
from core.containers.service_container import ServiceContainer
from core.containers.bot_container import BotContainer

logger = logging.getLogger(__name__)

async def init_app(app: FastAPI, settings: Config) -> None:
    """
    Initialize application dependencies and state.
    Args:
        app: FastAPI application instance
    """
    service_container = ServiceContainer.create(settings)
    bot_container = BotContainer.create(service_container)
    
    app.state.service_container = service_container
    logger.info("Service container initialized")
    
    app.state.bot_container = bot_container
    logger.info("Bot container initialized")
    
    
__all__ = (
    "init_app",
)

