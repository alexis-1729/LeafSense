from collections.abc import Iterator

import psycopg
from fastapi import Request

from app.core.config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_connection(request: Request) -> Iterator[psycopg.Connection]:
    settings: Settings = request.app.state.settings
    with psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
        autocommit=True,
    ) as connection:
        yield connection
