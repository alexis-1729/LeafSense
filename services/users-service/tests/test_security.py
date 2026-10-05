from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.security import get_current_claims
from app.main import app


def test_access_token_verifies_and_resolves_subject() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    user_id = uuid4()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "role": "user",
            "iss": "leafsense-auth",
            "aud": "leafsense-api",
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=15),
        },
        private_key,
        algorithm="RS256",
    )
    app.state.settings = Settings(
        database_host="unused",
        database_port=5432,
        database_name="unused",
        database_user="unused",
        database_password="unused",
        public_key_path="unused",
        internal_token_path="unused",
        jwt_issuer="leafsense-auth",
        jwt_audience="leafsense-api",
    )
    app.state.public_key = public_key

    from fastapi.security import HTTPAuthorizationCredentials
    from starlette.requests import Request

    scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "app": app,
    }
    request = Request(scope)
    claims = get_current_claims(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
        request,
    )

    assert claims["sub"] == str(user_id)
    assert claims["role"] == "user"


def test_invalid_signature_is_rejected() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "user",
            "iss": "leafsense-auth",
            "aud": "leafsense-api",
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=15),
        },
        private_key,
        algorithm="RS256",
    )
    app.state.settings = Settings(
        database_host="unused",
        database_port=5432,
        database_name="unused",
        database_user="unused",
        database_password="unused",
        public_key_path="unused",
        internal_token_path="unused",
        jwt_issuer="leafsense-auth",
        jwt_audience="leafsense-api",
    )
    app.state.public_key = other_key.public_key()

    from fastapi.security import HTTPAuthorizationCredentials
    from starlette.requests import Request

    request = Request(
        {
            "type": "http",
            "headers": [],
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "app": app,
        }
    )
    with pytest.raises(HTTPException) as error:
        get_current_claims(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
            request,
        )

    assert error.value.status_code == 401
