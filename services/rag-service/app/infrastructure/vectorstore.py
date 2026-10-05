from uuid import UUID, uuid5, NAMESPACE_URL

from qdrant_client import QdrantClient, models

from app.core.config import Settings


class QdrantVectorStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=10,
        )

    def ensure_collection(self) -> None:
        if self._client.collection_exists(self._settings.qdrant_collection):
            info = self._client.get_collection(self._settings.qdrant_collection)
            vectors = info.config.params.vectors
            if not isinstance(vectors, models.VectorParams):
                raise ValueError("Qdrant collection must use a single dense vector")
            if vectors.size != self._settings.embedding_dimension:
                raise ValueError(
                    "Qdrant collection dimension does not match embedding model; "
                    "migrate or recreate the collection before changing models"
                )
        else:
            self._client.create_collection(
                collection_name=self._settings.qdrant_collection,
                vectors_config=models.VectorParams(
                    size=self._settings.embedding_dimension,
                    distance=models.Distance.COSINE,
                ),
            )
        self._client.create_payload_index(
            collection_name=self._settings.qdrant_collection,
            field_name="doc_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        self._client.create_payload_index(
            collection_name=self._settings.qdrant_collection,
            field_name="pest_label",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

    @staticmethod
    def point_id(document_id: UUID, chunk_index: int) -> UUID:
        return uuid5(NAMESPACE_URL, f"leafsense:{document_id}:{chunk_index}")

    def upsert_document(
        self,
        document_id: UUID,
        chunks: list[str],
        vectors: list[list[float]],
        metadata: dict[str, str],
        expected_dimension: int,
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Each chunk must have exactly one embedding")
        if any(len(vector) != expected_dimension for vector in vectors):
            raise ValueError("Embedding dimension does not match Qdrant collection")
        self.ensure_collection()
        points = [
            models.PointStruct(
                id=self.point_id(document_id, index),
                vector=vector,
                payload={
                    **metadata,
                    "doc_id": str(document_id),
                    "chunk_idx": index,
                    "text": chunk,
                },
            )
            for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
        ]
        if points:
            self._client.upsert(
                collection_name=self._settings.qdrant_collection,
                points=points,
                wait=True,
            )
        if points:
            self._client.delete(
                collection_name=self._settings.qdrant_collection,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="doc_id",
                                match=models.MatchValue(value=str(document_id)),
                            ),
                            models.FieldCondition(
                                key="chunk_idx",
                                range=models.Range(gte=len(points)),
                            ),
                        ]
                    )
                ),
                wait=True,
            )

    def search(
        self,
        vector: list[float],
        pest_label: str,
        limit: int,
    ) -> list[dict[str, object]]:
        if len(vector) != self._settings.embedding_dimension:
            raise ValueError("Query embedding dimension does not match Qdrant collection")
        if limit <= 0:
            raise ValueError("Search limit must be positive")
        response = self._client.query_points(
            collection_name=self._settings.qdrant_collection,
            query=vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="pest_label",
                        match=models.MatchValue(value=pest_label),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
        )
        results: list[dict[str, object]] = []
        for point in response.points:
            payload = point.payload
            if payload is None:
                raise ValueError("Retrieved Qdrant point has no payload")
            text = payload.get("text")
            document_id = payload.get("doc_id")
            source = payload.get("source")
            crop = payload.get("crop")
            language = payload.get("language")
            if not all(
                isinstance(value, str)
                for value in (text, document_id, source, crop, language)
            ):
                raise ValueError("Retrieved Qdrant point has incomplete metadata")
            results.append(
                {
                    "doc_id": document_id,
                    "source": source,
                    "crop": crop,
                    "language": language,
                    "text": text,
                    "score": point.score,
                }
            )
        return results

    def delete_document(self, document_id: UUID) -> None:
        if not self._client.collection_exists(self._settings.qdrant_collection):
            return
        self._client.delete(
            collection_name=self._settings.qdrant_collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="doc_id",
                            match=models.MatchValue(value=str(document_id)),
                        )
                    ]
                )
            ),
            wait=True,
        )

    def close(self) -> None:
        self._client.close()
