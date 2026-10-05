import hashlib
import json
import secrets
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from jwt.algorithms import RSAAlgorithm

from app.core.config import Settings


def load_key_pair(settings: Settings) -> tuple[RSAPrivateKey, RSAPublicKey]:
    private_key = serialization.load_pem_private_key(
        Path(settings.private_key_path).read_bytes(),
        password=None,
    )
    public_key = serialization.load_pem_public_key(
        Path(settings.public_key_path).read_bytes(),
    )
    if not isinstance(private_key, RSAPrivateKey):
        raise ValueError("JWT private key must be RSA")
    if not isinstance(public_key, RSAPublicKey):
        raise ValueError("JWT public key must be RSA")
    if private_key.public_key().public_numbers() != public_key.public_numbers():
        raise ValueError("JWT public and private keys do not match")
    return private_key, public_key


def load_internal_token(token_path: str) -> str:
    token = Path(token_path).read_text(encoding="utf-8").strip()
    if len(token) < 32:
        raise ValueError("Internal service token must contain at least 32 characters")
    return token


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def create_jwks(
    public_key: RSAPublicKey,
    key_id: str,
) -> dict[str, list[dict[str, object]]]:
    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk.update({"kid": key_id, "use": "sig", "alg": "RS256"})
    return {"keys": [jwk]}
