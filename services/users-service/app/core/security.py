import hmac
from pathlib import Path
from typing import Annotated
from uuid import UUID

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings

bearer_scheme = HTTPBearer(auto_error=False)


def load_public_key(settings: Settings) -> RSAPublicKey:
    public_key = serialization.load_pem_public_key(
        Path(settings.public_key_path).read_bytes(),
    )
    if not isinstance(public_key, RSAPublicKey):
        raise ValueError("JWT public key must be RSA")
    return public_key


def load_internal_token(token_path: str) -> str:
    token = Path(token_path).read_text(encoding="utf-8").strip()
    if len(token) < 32:
        raise ValueError("Internal service token must contain at least 32 characters")
    return token


def get_current_claims(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    request: Request,
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings: Settings = request.app.state.settings
    try:
        claims = jwt.decode(
            credentials.credentials,
            request.app.state.public_key,
            algorithms=["RS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "role", "iss", "aud", "exp", "iat", "nbf"]},
        )
        UUID(claims["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return claims


def require_internal_service(
    request: Request,
    supplied_token: str | None,
) -> None:
    expected_token: str = request.app.state.internal_token
    if supplied_token is None or not hmac.compare_digest(supplied_token, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid internal service token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
