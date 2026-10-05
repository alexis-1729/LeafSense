import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    public_key_path: str
    internal_token_path: str
    jwt_issuer: str
    jwt_audience: str


def get_settings() -> Settings:
    return Settings(
        database_host=os.getenv("DB_HOST", "postgres"),
        database_port=int(os.getenv("DB_PORT", "5432")),
        database_name=os.getenv("DB_NAME", "users_db"),
        database_user=os.getenv("DB_USER", "users_app"),
        database_password=os.environ["DB_PASSWORD"],
        public_key_path=os.getenv(
            "JWT_PUBLIC_KEY_PATH",
            "/run/secrets/jwt_public_key",
        ),
        internal_token_path=os.getenv(
            "INTERNAL_SERVICE_TOKEN_PATH",
            "/run/secrets/internal_service_token",
        ),
        jwt_issuer=os.getenv("JWT_ISSUER", "leafsense-auth"),
        jwt_audience=os.getenv("JWT_AUDIENCE", "leafsense-api"),
    )
