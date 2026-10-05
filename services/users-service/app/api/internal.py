from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from psycopg.errors import UniqueViolation

from app.api.deps import UserServiceDependency, get_connection
from app.core.security import require_internal_service
from app.schemas.users import InternalUserCreate, UserResponse
from app.services.user_service import ProfileConflictError

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_profile(
    payload: InternalUserCreate,
    request: Request,
    service: UserServiceDependency,
    connection: Annotated[psycopg.Connection, Depends(get_connection)],
    internal_token: Annotated[str | None, Header(alias="X-Internal-Service-Token")] = None,
) -> UserResponse:
    require_internal_service(request, internal_token)
    try:
        with connection.transaction():
            profile = service.ensure_profile(
                payload.user_id,
                str(payload.email).lower(),
            )
    except ProfileConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile identity conflicts with an existing user",
        ) from exc
    except UniqueViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already assigned to another profile",
        ) from exc
    return UserResponse(**profile.__dict__)
