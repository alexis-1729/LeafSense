from uuid import uuid4

from app.infrastructure.vectorstore import QdrantVectorStore


def test_point_ids_are_deterministic_by_document_and_chunk() -> None:
    document_id = uuid4()

    assert QdrantVectorStore.point_id(document_id, 0) == QdrantVectorStore.point_id(
        document_id,
        0,
    )
    assert QdrantVectorStore.point_id(document_id, 0) != QdrantVectorStore.point_id(
        document_id,
        1,
    )
