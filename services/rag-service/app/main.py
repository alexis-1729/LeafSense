from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import psycopg
from fastapi import FastAPI

from app.api import diagnosis, documents, health
from app.core.config import Settings, get_settings
from app.core.security import load_public_key
from app.infrastructure.document_extractor import DocumentExtractor
from app.infrastructure.embeddings import LocalEmbedder
from app.infrastructure.analysis_client import AnalysisServiceClient
from app.infrastructure.llm.openai_compatible import OpenAICompatibleLLM
from app.infrastructure.persistence.session import connect
from app.infrastructure.vectorstore import QdrantVectorStore


def _run_migrations(settings: Settings) -> None:
    migrations = Path(__file__).parent.parent / "migrations"
    with connect(settings) as connection:
        for migration in sorted(migrations.glob("*.sql")):
            connection.execute(migration.read_text(encoding="utf-8"))


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    public_key = load_public_key(settings)
    _run_migrations(settings)
    vector_store = QdrantVectorStore(settings)
    analysis_http_client = httpx.AsyncClient(timeout=30.0)
    llm_http_client = httpx.AsyncClient(timeout=settings.llm_timeout_seconds)
    try:
        vector_store.ensure_collection()
        embedder = LocalEmbedder(settings.embedding_model, settings.embedding_cache)
        embedder.validate_dimension(settings.embedding_dimension)
        application.state.settings = settings
        application.state.public_key = public_key
        application.state.vector_store = vector_store
        application.state.embedder = embedder
        application.state.analysis_client = AnalysisServiceClient(
            settings.analysis_service_url,
            analysis_http_client,
        )
        application.state.llm = OpenAICompatibleLLM(
            settings.llm_base_url,
            settings.llm_model,
            settings.llm_api_key,
            llm_http_client,
        )
        application.state.document_extractor = DocumentExtractor()
        application.state.connection_factory = connect
        yield
    finally:
        vector_store.close()
        await analysis_http_client.aclose()
        await llm_http_client.aclose()


app = FastAPI(title="LeafSense RAG Service", version="1.0.0", lifespan=lifespan)
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(diagnosis.router)
