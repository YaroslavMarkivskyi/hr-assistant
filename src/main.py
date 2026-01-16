import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from api.routes import router
from config import settings

from core.bootstrap import init_app
from core.factory import register_routers

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("🚀 Initializing application...")
    await init_app(app, settings)
    yield
    logger.info("🛑 FastAPI application shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)


register_routers(app)


@app.get("/")
async def root():
    return {
        "status": "running",
        "version": settings.PROJECT_VERSION,
        "service": settings.PROJECT_NAME
    }

