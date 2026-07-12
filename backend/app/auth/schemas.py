from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.auth.models import UserRoleName
from app.shared.models.base import UserStatus


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.lower().strip()
        if "@" not in normalized:
            raise ValueError("Invalid email format")
        local_part, domain = normalized.rsplit("@", 1)
        if not local_part or not domain or "." not in domain:
            raise ValueError("Invalid email format")
        return normalized


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RoleResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class PermissionResponse(BaseModel):
    id: UUID
    code: str
    name: str
    module: str

    model_config = {"from_attributes": True}


class EmployeeSummary(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    designation: str | None
    department_id: UUID | None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: UUID
    email: str
    status: UserStatus
    last_login: datetime | None
    roles: list[RoleResponse]
    permissions: list[str]
    employee: EmployeeSummary | None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    user: UserResponse


class AuthenticatedUser(BaseModel):
    id: UUID
    email: str
    status: UserStatus
    role_names: list[UserRoleName]
    permission_codes: list[str]
    employee_id: UUID | None

    def has_permission(self, permission_code: str) -> bool:
        return permission_code in self.permission_codes

    def has_role(self, role_name: UserRoleName) -> bool:
        return role_name in self.role_names
