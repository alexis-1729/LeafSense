from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Credential:
    user_id: UUID
    email: str
    password_hash: str
    role: str
    profile_status: str
