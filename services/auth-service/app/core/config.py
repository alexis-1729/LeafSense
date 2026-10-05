import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    private_key_path: str
    public_key_path: str
    internal_token_path: str
    jwt_issuer: str
    jwt_audience: str
    jwt_key_id: str
    access_token_minutes: int
    refresh_token_days: int
    users_service_url: str


def get_settings() -> Settings:
    settings = Settings(
        database_host=os.getenv("DB_HOST", "postgres"),
        database_port=int(os.getenv("DB_PORT", "5432")),
        database_name=os.getenv("DB_NAME", "auth_db"),
        database_user=os.getenv("DB_USER", "auth_app"),
        database_password=os.environ["DB_PASSWORD"],
        private_key_path=os.getenv(
            "JWT_PRIVATE_KEY_PATH",
            "/run/secrets/jwt_private_key",
        ),
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
        jwt_key_id=os.getenv("JWT_KEY_ID", "leafsense-key-1"),
        access_token_minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "15")),
        refresh_token_days=int(os.getenv("REFRESH_TOKEN_DAYS", "14")),
        users_service_url=os.getenv(
            "USERS_SERVICE_URL",
            "http://users:8000",
        ).rstrip("/"),
    )
    if settings.access_token_minutes <= 0:
        raise ValueError("ACCESS_TOKEN_MINUTES must be positive")
    if not 7 <= settings.refresh_token_days <= 30:
        raise ValueError("REFRESH_TOKEN_DAYS must be between 7 and 30")
    return settings
