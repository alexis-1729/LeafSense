from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row


class DocumentRepository:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def create(
        self,
        text: str,
        pest_label: str,
        crop: str,
        source: str,
        language: str,
        filename: str,
    ) -> dict:
        document_id = uuid4()
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO documents (
                    id, content, pest_label, crop, source, language, filename, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                RETURNING id, status
                """,
                (document_id, text, pest_label, crop, source, language, filename),
            )
            row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Document insert did not return a document")
        return row

    def get_status(self, document_id: UUID) -> dict | None:
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, pest_label, crop, source, language, filename, status, error,
                       chunk_count, created_at, updated_at
                FROM documents
                WHERE id = %s
                """,
                (document_id,),
            )
            return cursor.fetchone()

    def claim_next(self, lease_seconds: int) -> dict | None:
        with self._connection.transaction():
            with self._connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    WITH candidate AS (
                        SELECT id
                        FROM documents
                        WHERE status = 'pending'
                           OR (status = 'processing' AND updated_at <
                               now() - (%s * interval '1 second'))
                        ORDER BY created_at
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                    )
                    UPDATE documents AS document
                    SET status = 'processing',
                        error = NULL,
                        updated_at = now()
                    FROM candidate
                    WHERE document.id = candidate.id
                    RETURNING document.id, document.content, document.pest_label,
                              document.crop, document.source, document.language
                    """,
                    (lease_seconds,),
                )
                return cursor.fetchone()

    def is_processing(self, document_id: UUID) -> bool:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM documents WHERE id = %s AND status = 'processing'",
                (document_id,),
            )
            return cursor.fetchone() is not None

    def mark_indexed(self, document_id: UUID, chunk_count: int) -> bool:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE documents
                SET status = 'indexed', chunk_count = %s, error = NULL, updated_at = now()
                WHERE id = %s AND status = 'processing'
                """,
                (chunk_count, document_id),
            )
            return cursor.rowcount == 1

    def mark_failed(self, document_id: UUID, error: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE documents
                SET status = 'failed', error = %s, updated_at = now()
                WHERE id = %s AND status = 'processing'
                """,
                (error[:1000], document_id),
            )

    def mark_deleting(self, document_id: UUID) -> dict | None:
        with self._connection.transaction():
            with self._connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT status, pest_label
                    FROM documents
                    WHERE id = %s AND status <> 'deleting'
                    FOR UPDATE
                    """,
                    (document_id,),
                )
                previous = cursor.fetchone()
                if previous is None:
                    return None
                cursor.execute(
                    """
                    UPDATE documents
                    SET status = 'deleting', updated_at = now()
                    WHERE id = %s
                    """,
                    (document_id,),
                )
                return previous

    def restore_status(self, document_id: UUID, previous_status: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE documents
                SET status = %s, updated_at = now()
                WHERE id = %s AND status = 'deleting'
                """,
                (previous_status, document_id),
            )

    def delete(self, document_id: UUID) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
