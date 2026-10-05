from contextlib import asynccontextmanager
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.v2 import health, infer, models
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.model.predictor import load_predictor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    logger.info("Loading pest classifier")
    application.state.predictor = load_predictor(settings)
    yield
    application.state.predictor = None


app = FastAPI(
    title="LeafSense Analysis Service",
    version="2.0.0",
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(models.router)
app.include_router(infer.router)
