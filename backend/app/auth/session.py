from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.auth.schemas import UserResponse


class SessionInfo(BaseModel):
    user_id: UUID
    email: str
    roles: list[str]
    permissions: list[str]
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    is_active: bool = True


class SessionResponse(BaseModel):
    session: SessionInfo
    user: UserResponse
