import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from psycopg.errors import UniqueViolation

from app.api.deps import get_connection
from app.core.security import hash_refresh_token
from app.repositories.credential_repo import CredentialRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegistrationResponse,
    TokenPair,
)
from app.services.password_hasher import (
    DUMMY_PASSWORD_HASH,
    hash_password,
    verify_password,
)
from app.services.token_service import TokenService
from app.services.users_client import UsersServiceError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


def _token_service(request: Request, connection: psycopg.Connection) -> TokenService:
    return TokenService(
        request.app.state.settings,
        request.app.state.private_key,
        RefreshTokenRepository(connection),
    )


def _token_pair(
    service: TokenService,
    user_id: UUID,
    role: str,
    refresh_token: str,
) -> TokenPair:
    return TokenPair(
        access_token=service.create_access_token(user_id, role),
        refresh_token=refresh_token,
        expires_in=service.access_token_lifetime_seconds,
    )


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    request: Request,
    connection: psycopg.Connection = Depends(get_connection),
) -> RegistrationResponse:
    email = str(payload.email).lower()
    credentials = CredentialRepository(connection)
    credential = credentials.get_by_email(email)

    if credential is None:
        user_id = uuid4()
        try:
            with connection.transaction():
                credentials.create_pending(
                    user_id,
                    email,
                    hash_password(payload.password.get_secret_value()),
                )
        except UniqueViolation as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            ) from exc
        credential = credentials.get_by_id(user_id)
        if credential is None:
            raise RuntimeError("Credential insert did not create a credential")
    elif credential.profile_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    elif not verify_password(
        payload.password.get_secret_value(),
        credential.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    try:
        request.app.state.users_client.ensure_user(
            str(credential.user_id),
            credential.email,
        )
    except UsersServiceError as exc:
        logger.warning(
            "Profile provisioning remains pending for user_id=%s: %s",
            credential.user_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile provisioning is pending; retry registration shortly",
            headers={"Retry-After": "3"},
        ) from exc

    with connection.transaction():
        credentials.mark_profile_ready(credential.user_id)
    return RegistrationResponse(
        user_id=credential.user_id,
        email=credential.email,
        status="ready",
    )


@router.post("/login", response_model=TokenPair)
def login(
    payload: LoginRequest,
    request: Request,
    connection: psycopg.Connection = Depends(get_connection),
) -> TokenPair:
    credentials = CredentialRepository(connection)
    credential = credentials.get_by_email(str(payload.email).lower())
    hashed_password = credential.password_hash if credential else DUMMY_PASSWORD_HASH
    password_matches = verify_password(
        payload.password.get_secret_value(),
        hashed_password,
    )
    if credential is None or not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credential.profile_status != "ready":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile provisioning is pending",
            headers={"Retry-After": "3"},
        )

    service = _token_service(request, connection)
    with connection.transaction():
        refresh_token = service.create_refresh_token(credential.user_id)
    return _token_pair(service, credential.user_id, credential.role, refresh_token)


@router.post("/refresh", response_model=TokenPair)
def refresh(
    payload: RefreshRequest,
    request: Request,
    connection: psycopg.Connection = Depends(get_connection),
) -> TokenPair:
    token_hash = hash_refresh_token(payload.refresh_token.get_secret_value())
    repository = RefreshTokenRepository(connection)
    service = _token_service(request, connection)
    now = datetime.now(UTC)
    failure: str | None = None
    access_token: str | None = None
    rotated_token: str | None = None

    with connection.transaction():
        record = repository.get_for_update(token_hash)
        if record is None:
            failure = "Invalid refresh token"
        elif record.revoked_at is not None:
            repository.revoke_family(record.family_id)
            failure = "Refresh token reuse detected; token family revoked"
        elif record.expires_at <= now:
            repository.revoke_family(record.family_id)
            failure = "Refresh token has expired"
        else:
            credential = CredentialRepository(connection).get_by_id(record.user_id)
            if credential is None or credential.profile_status != "ready":
                repository.revoke_family(record.family_id)
                failure = "Account is not active"
            else:
                rotated_token = service.create_refresh_token(
                    record.user_id,
                    record.family_id,
                )
                repository.revoke(token_hash, hash_refresh_token(rotated_token))
                access_token = service.create_access_token(
                    record.user_id,
                    credential.role,
                )

    if failure is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=failure,
        )
    if access_token is None or rotated_token is None:
        raise RuntimeError("Refresh token rotation completed without issuing a token pair")
    return TokenPair(
        access_token=access_token,
        refresh_token=rotated_token,
        expires_in=service.access_token_lifetime_seconds,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    connection: psycopg.Connection = Depends(get_connection),
) -> Response:
    token_hash = hash_refresh_token(payload.refresh_token.get_secret_value())
    with connection.transaction():
        RefreshTokenRepository(connection).revoke_family_for_token(token_hash)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
