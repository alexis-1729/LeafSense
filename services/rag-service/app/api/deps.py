from collections.abc import Iterator
from typing import Annotated

import psycopg
from fastapi import Depends, Request

from app.core.config import Settings
from app.core.security import get_current_claims, require_admin


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


AdminClaims = Annotated[dict, Depends(require_admin)]
CurrentClaims = Annotated[dict, Depends(get_current_claims)]
