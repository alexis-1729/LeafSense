from datetime import datetime
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.models.refresh_token import RefreshTokenRecord


class RefreshTokenRepository:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def create(
        self,
        token_hash: str,
        family_id: UUID,
        user_id: UUID,
        expires_at: datetime,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO refresh_tokens
                    (token_hash, family_id, user_id, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (token_hash, family_id, user_id, expires_at),
            )

    def get_for_update(self, token_hash: str) -> RefreshTokenRecord | None:
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT token_hash, family_id, user_id, expires_at, revoked_at
                FROM refresh_tokens
                WHERE token_hash = %s
                FOR UPDATE
                """,
                (token_hash,),
            )
            row = cursor.fetchone()
        return RefreshTokenRecord(**row) if row else None

    def revoke(self, token_hash: str, replaced_by_hash: str | None = None) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revoked_at = COALESCE(revoked_at, now()),
                    replaced_by_hash = COALESCE(%s, replaced_by_hash)
                WHERE token_hash = %s
                """,
                (replaced_by_hash, token_hash),
            )

    def revoke_family(self, family_id: UUID) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revoked_at = COALESCE(revoked_at, now())
                WHERE family_id = %s
                """,
                (family_id,),
            )

    def revoke_family_for_token(self, token_hash: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revoked_at = COALESCE(revoked_at, now())
                WHERE family_id = (
                    SELECT family_id
                    FROM refresh_tokens
                    WHERE token_hash = %s
                )
                """,
                (token_hash,),
            )
