from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.repository import AuthRepository
from app.auth.schemas import AuthenticatedUser
from app.auth.service import AuthService
from app.core.database import get_db
from app.core.security import decode_token
from app.shared.exceptions.base import UnauthorizedError, ValidationError

security_scheme = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    cached_user = getattr(request.state, "authenticated_user", None)
    if isinstance(cached_user, AuthenticatedUser):
        return cached_user

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Authentication credentials were not provided")

    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise UnauthorizedError("Invalid or expired access token") from exc

    if payload.get("type") != "access":
        raise ValidationError("Token is not an access token")

    user_id = UUID(payload["sub"])
    repository = AuthRepository(db)
    user = repository.require_user(user_id)

    if user.status.value != "ACTIVE":
        raise UnauthorizedError("User account is not active")

    service = AuthService(db)
    authenticated_user = service.build_authenticated_user(user)
    request.state.authenticated_user = authenticated_user
    return authenticated_user


def require_permission(permission_code: str):
    def permission_checker(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
    ) -> AuthenticatedUser:
        from app.auth.permissions import PermissionCode

        try:
            permission = PermissionCode(permission_code)
        except ValueError as exc:
            raise ValidationError(f"Unknown permission: {permission_code}") from exc

        auth_service.require_permission(current_user, permission)
        return current_user

    return permission_checker


def get_optional_refresh_token(
    refresh_token: Annotated[str | None, Header(alias="X-Refresh-Token")] = None,
) -> str | None:
    return refresh_token
