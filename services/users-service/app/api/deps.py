from collections.abc import Iterator
from typing import Annotated

import psycopg
from fastapi import Depends, Request

from app.core.config import Settings
from app.core.security import get_current_claims
from app.services.user_service import UserService


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


def get_user_service(
    connection: Annotated[psycopg.Connection, Depends(get_connection)],
) -> UserService:
    from app.repositories.user_repo import UserRepository

    return UserService(UserRepository(connection))


CurrentClaims = Annotated[dict, Depends(get_current_claims)]
UserServiceDependency = Annotated[UserService, Depends(get_user_service)]
