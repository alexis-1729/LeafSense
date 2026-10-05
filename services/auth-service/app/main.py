from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from pathlib import Path

import httpx
import psycopg
from fastapi import FastAPI

from app.api import auth, jwks
from app.core.config import Settings, get_settings
from app.core.security import load_internal_token, load_key_pair
from app.services.users_client import UsersClient

logger = logging.getLogger(__name__)


def _connect(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
        autocommit=True,
    )


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    private_key, public_key = load_key_pair(settings)
    internal_token = load_internal_token(settings.internal_token_path)
    with _connect(settings) as connection:
        migration = Path(__file__).parent.parent / "migrations" / "001_initial.sql"
        connection.execute(migration.read_text(encoding="utf-8"))

    http_client = httpx.Client(timeout=httpx.Timeout(3.0))
    application.state.settings = settings
    application.state.private_key = private_key
    application.state.public_key = public_key
    application.state.users_client = UsersClient(
        settings.users_service_url,
        internal_token,
        http_client,
    )
    logger.info("Auth service started")
    try:
        yield
    finally:
        http_client.close()


app = FastAPI(title="LeafSense Auth Service", version="1.0.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(jwks.router)


@app.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready", tags=["health"])
def ready() -> dict[str, str]:
    settings = get_settings()
    with _connect(settings) as connection:
        connection.execute("SELECT 1")
    return {"status": "ready"}
