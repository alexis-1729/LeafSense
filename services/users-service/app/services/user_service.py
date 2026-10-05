from uuid import UUID

from app.models.user_profile import UserProfile
from app.repositories.user_repo import UserRepository


class ProfileConflictError(ValueError):
    pass


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def ensure_profile(self, user_id: UUID, email: str) -> UserProfile:
        try:
            return self._repository.create_if_missing(user_id, email)
        except ValueError as exc:
            raise ProfileConflictError(str(exc)) from exc

    def get_profile(self, user_id: UUID) -> UserProfile | None:
        return self._repository.get_by_id(user_id)

    def update_display_name(
        self,
        user_id: UUID,
        display_name: str | None,
    ) -> UserProfile | None:
        return self._repository.update_display_name(user_id, display_name)
