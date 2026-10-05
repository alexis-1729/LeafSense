from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Jsonb


class DiagnosisRepository:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def create(
        self,
        user_id: UUID,
        crop: str | None,
        pest_label: str,
        confidence: float,
        top_k: list[dict[str, object]],
        conclusive: bool,
        diagnosis: dict[str, object] | None,
        sources: list[dict[str, object]],
    ) -> UUID:
        diagnosis_id = uuid4()
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO diagnoses (
                    id, user_id, crop, pest_label, confidence, top_k,
                    conclusive, diagnosis, sources
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    diagnosis_id,
                    user_id,
                    crop,
                    pest_label,
                    confidence,
                    Jsonb(top_k),
                    conclusive,
                    Jsonb(diagnosis) if diagnosis is not None else None,
                    Jsonb(sources),
                ),
            )
        return diagnosis_id
