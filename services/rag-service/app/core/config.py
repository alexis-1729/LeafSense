import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str
    embedding_model: str
    embedding_dimension: int
    embedding_cache: str
    max_document_bytes: int
    max_image_bytes: int
    chunk_size: int
    chunk_overlap: int
    worker_poll_seconds: float
    worker_lease_seconds: int
    analysis_service_url: str
    diagnosis_confidence_threshold: float
    llm_base_url: str
    llm_model: str
    llm_api_key: str
    llm_timeout_seconds: float
    public_key_path: str
    jwt_issuer: str
    jwt_audience: str


def get_settings() -> Settings:
    settings = Settings(
        database_host=os.getenv("DB_HOST", "postgres"),
        database_port=int(os.getenv("DB_PORT", "5432")),
        database_name=os.getenv("DB_NAME", "rag_db"),
        database_user=os.getenv("DB_USER", "rag_app"),
        database_password=os.environ["DB_PASSWORD"],
        qdrant_url=os.getenv("QDRANT_URL", "http://qdrant:6333"),
        qdrant_api_key=os.environ["QDRANT_API_KEY"],
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "leafsense_documents"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
        embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
        embedding_cache=os.getenv("HF_HOME", "/model-cache"),
        max_document_bytes=int(os.getenv("MAX_DOCUMENT_BYTES", str(10 * 1024 * 1024))),
        max_image_bytes=int(os.getenv("MAX_IMAGE_BYTES", str(10 * 1024 * 1024))),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
        worker_poll_seconds=float(os.getenv("WORKER_POLL_SECONDS", "2")),
        worker_lease_seconds=int(os.getenv("WORKER_LEASE_SECONDS", "300")),
        analysis_service_url=os.getenv(
            "ANALYSIS_SERVICE_URL",
            "http://analysis:8000",
        ).rstrip("/"),
        diagnosis_confidence_threshold=float(
            os.getenv("DIAGNOSIS_CONFIDENCE_THRESHOLD", "0.60")
        ),
        llm_base_url=os.getenv(
            "LLM_BASE_URL",
            "https://api.openai.com/v1",
        ).rstrip("/"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
        public_key_path=os.getenv(
            "JWT_PUBLIC_KEY_PATH",
            "/run/secrets/jwt_public_key",
        ),
        jwt_issuer=os.getenv("JWT_ISSUER", "leafsense-auth"),
        jwt_audience=os.getenv("JWT_AUDIENCE", "leafsense-api"),
    )
    if settings.embedding_dimension <= 0:
        raise ValueError("EMBEDDING_DIMENSION must be positive")
    if settings.max_document_bytes <= 0:
        raise ValueError("MAX_DOCUMENT_BYTES must be positive")
    if settings.max_image_bytes <= 0:
        raise ValueError("MAX_IMAGE_BYTES must be positive")
    if settings.chunk_size <= 0 or not 0 <= settings.chunk_overlap < settings.chunk_size:
        raise ValueError("Chunk overlap must be non-negative and smaller than chunk size")
    if settings.worker_poll_seconds <= 0 or settings.worker_lease_seconds <= 0:
        raise ValueError("Worker polling and lease values must be positive")
    if not 0.0 <= settings.diagnosis_confidence_threshold <= 1.0:
        raise ValueError("DIAGNOSIS_CONFIDENCE_THRESHOLD must be between 0 and 1")
    if settings.llm_timeout_seconds <= 0:
        raise ValueError("LLM_TIMEOUT_SECONDS must be positive")
    if not settings.llm_model:
        raise ValueError("LLM_MODEL must not be empty")
    return settings
