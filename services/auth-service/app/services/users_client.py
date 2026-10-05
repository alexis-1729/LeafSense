import httpx


class UsersServiceError(Exception):
    pass


class UsersClient:
    def __init__(
        self,
        base_url: str,
        internal_token: str,
        client: httpx.Client,
    ) -> None:
        self._base_url = base_url
        self._internal_token = internal_token
        self._client = client

    def ensure_user(self, user_id: str, email: str) -> None:
        try:
            response = self._client.post(
                f"{self._base_url}/internal/users",
                json={"user_id": user_id, "email": email},
                headers={"X-Internal-Service-Token": self._internal_token},
            )
        except httpx.HTTPError as exc:
            raise UsersServiceError("Users service is unavailable") from exc
        if response.status_code not in (200, 201):
            raise UsersServiceError(
                f"Users service rejected profile creation ({response.status_code})"
            )
