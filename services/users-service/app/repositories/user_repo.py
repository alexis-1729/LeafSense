from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.models.user_profile import UserProfile


class UserRepository:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def get_by_id(self, user_id: UUID) -> UserProfile | None:
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT user_id, email, display_name, created_at, updated_at
                FROM user_profiles
                WHERE user_id = %s
                """,
                (user_id,),
            )
            row = cursor.fetchone()
        return UserProfile(**row) if row else None

    def create_if_missing(self, user_id: UUID, email: str) -> UserProfile:
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO user_profiles (user_id, email)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO NOTHING
                """,
                (user_id, email),
            )
        profile = self.get_by_id(user_id)
        if profile is None:
            raise RuntimeError("Profile insert did not create or find a profile")
        if profile.email != email:
            raise ValueError("user_id already exists with a different email")
        return profile

    def update_display_name(
        self,
        user_id: UUID,
        display_name: str | None,
    ) -> UserProfile | None:
        with self._connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE user_profiles
                SET display_name = %s, updated_at = now()
                WHERE user_id = %s
                RETURNING user_id, email, display_name, created_at, updated_at
                """,
                (display_name, user_id),
            )
            row = cursor.fetchone()
        return UserProfile(**row) if row else None
