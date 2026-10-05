from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class RefreshTokenRecord:
    token_hash: str
    family_id: UUID
    user_id: UUID
    expires_at: datetime
    revoked_at: datetime | None
