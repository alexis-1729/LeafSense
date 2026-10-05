from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from app.core.config import Settings
from app.core.security import hash_refresh_token, new_refresh_token
from app.repositories.refresh_token_repo import RefreshTokenRepository


class TokenService:
    def __init__(
        self,
        settings: Settings,
        private_key: RSAPrivateKey,
        refresh_tokens: RefreshTokenRepository,
    ) -> None:
        self._settings = settings
        self._private_key = private_key
        self._refresh_tokens = refresh_tokens

    @property
    def access_token_lifetime_seconds(self) -> int:
        return self._settings.access_token_minutes * 60

    def create_access_token(self, user_id: UUID, role: str) -> str:
        now = datetime.now(UTC)
        claims = {
            "sub": str(user_id),
            "role": role,
            "iss": self._settings.jwt_issuer,
            "aud": self._settings.jwt_audience,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=self._settings.access_token_minutes),
            "jti": str(uuid4()),
        }
        return jwt.encode(
            claims,
            self._private_key,
            algorithm="RS256",
            headers={"kid": self._settings.jwt_key_id, "typ": "JWT"},
        )

    def create_refresh_token(
        self,
        user_id: UUID,
        family_id: UUID | None = None,
    ) -> str:
        token = new_refresh_token()
        self._refresh_tokens.create(
            hash_refresh_token(token),
            family_id or uuid4(),
            user_id,
            datetime.now(UTC) + timedelta(days=self._settings.refresh_token_days),
        )
        return token
