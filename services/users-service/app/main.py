from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from fastapi import FastAPI

from app.api import internal, users
from app.core.config import Settings, get_settings
from app.core.security import load_internal_token, load_public_key


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
    public_key = load_public_key(settings)
    internal_token = load_internal_token(settings.internal_token_path)
    with _connect(settings) as connection:
        migration = Path(__file__).parent.parent / "migrations" / "001_initial.sql"
        connection.execute(migration.read_text(encoding="utf-8"))
    application.state.settings = settings
    application.state.public_key = public_key
    application.state.internal_token = internal_token
    yield


app = FastAPI(title="LeafSense Users Service", version="1.0.0", lifespan=lifespan)
app.include_router(users.router)
app.include_router(internal.router)


@app.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready", tags=["health"])
def ready() -> dict[str, str]:
    settings = get_settings()
    with _connect(settings) as connection:
        connection.execute("SELECT 1")
    return {"status": "ready"}
