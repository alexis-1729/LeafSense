from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.models.credential import Credential


class CredentialRepository:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def get_by_email(self, email: str) -> Credential | None:
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT user_id, email, password_hash, role, profile_status
                FROM credentials
                WHERE email = %s
                """,
                (email,),
            )
            row = cursor.fetchone()
        return Credential(**row) if row else None

    def get_by_id(self, user_id: UUID) -> Credential | None:
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT user_id, email, password_hash, role, profile_status
                FROM credentials
                WHERE user_id = %s
                """,
                (user_id,),
            )
            row = cursor.fetchone()
        return Credential(**row) if row else None

    def create_pending(
        self,
        user_id: UUID,
        email: str,
        password_hash: str,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO credentials (user_id, email, password_hash, role)
                VALUES (%s, %s, %s, 'user')
                """,
                (user_id, email, password_hash),
            )

    def mark_profile_ready(self, user_id: UUID) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE credentials
                SET profile_status = 'ready'
                WHERE user_id = %s
                """,
                (user_id,),
            )

