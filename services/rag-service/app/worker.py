import logging
import time
from pathlib import Path

import psycopg

from app.core.config import Settings, get_settings
from app.infrastructure.chunking import chunk_text
from app.infrastructure.embeddings import LocalEmbedder
from app.infrastructure.persistence.document_repo import DocumentRepository
from app.infrastructure.persistence.session import connect
from app.infrastructure.vectorstore import QdrantVectorStore

logger = logging.getLogger(__name__)


def run_worker(settings: Settings) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    embedder = LocalEmbedder(settings.embedding_model, settings.embedding_cache)
    logger.info("Loading local embedding model %s", settings.embedding_model)
    embedder.validate_dimension(settings.embedding_dimension)
    vector_store = QdrantVectorStore(settings)
    vector_store.ensure_collection()
    logger.info("Document worker started")
    try:
        while True:
            with connect(settings) as connection:
                repository = DocumentRepository(connection)
                document = repository.claim_next(settings.worker_lease_seconds)
                if document is None:
                    time.sleep(settings.worker_poll_seconds)
                    continue
                document_id = document["id"]
                try:
                    chunks = chunk_text(
                        document["content"],
                        settings.chunk_size,
                        settings.chunk_overlap,
                    )
                    if not chunks:
                        raise ValueError("Document contains no indexable text")
                    vectors = embedder.embed_documents(chunks)
                    if not repository.is_processing(document_id):
                        continue
                    vector_store.upsert_document(
                        document_id=document_id,
                        chunks=chunks,
                        vectors=vectors,
                        metadata={
                            "pest_label": document["pest_label"],
                            "crop": document["crop"],
                            "source": document["source"],
                            "language": document["language"],
                        },
                        expected_dimension=settings.embedding_dimension,
                    )
                    if not repository.mark_indexed(document_id, len(chunks)):
                        vector_store.delete_document(document_id)
                except Exception as exc:
                    logger.exception("Indexing failed for document_id=%s", document_id)
                    try:
                        vector_store.delete_document(document_id)
                    except Exception:
                        logger.exception(
                            "Could not remove partial vectors for document_id=%s",
                            document_id,
                        )
                    repository.mark_failed(document_id, str(exc))
    finally:
        vector_store.close()


def main() -> None:
    run_worker(get_settings())


if __name__ == "__main__":
    main()
