import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from core.config import settings

from core.bootstrap import init_app
from core.factory import register_routers

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s|%(name)s|%(funcName)s|%(lineno)d|%(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Initializing application...")
    await init_app(app, settings)
    yield
    logger.info("FastAPI application shutting down")
    
    # TODO: Add any necessary cleanup logic here


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

