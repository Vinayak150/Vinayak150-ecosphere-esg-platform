from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.events import publish_user_logged_in, publish_user_logged_out
from app.auth.models import User, UserRoleName
from app.auth.permissions import PermissionCode
from app.auth.repository import AuthRepository
from app.auth.schemas import (
    AuthenticatedUser,
    EmployeeSummary,
    LoginRequest,
    RoleResponse,
    TokenResponse,
    UserResponse,
)
from app.auth.session import SessionInfo, SessionResponse
from app.auth.validators import normalize_email
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.shared.exceptions.base import (
    BusinessRuleViolationError,
    UnauthorizedError,
    ValidationError,
)
from app.shared.models.base import UserStatus
from app.shared.services.activity_log import ActivityLogService

settings = get_settings()


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repository = AuthRepository(db)
        self._activity_log = ActivityLogService(db)

    def login(self, request: LoginRequest) -> TokenResponse:
        email = normalize_email(request.email)
        user = self._repository.get_user_by_email(email)
        if user is None or not verify_password(request.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise BusinessRuleViolationError("User account is not active")

        self._repository.update_last_login(user)
        tokens = self._issue_tokens(user)

        self._activity_log.log_mutation(
            employee_id=user.employee.id if user.employee else None,
            user_id=user.id,
            action="LOGIN",
            entity="user",
            entity_id=user.id,
        )
        publish_user_logged_in({"user_id": str(user.id), "email": user.email})
        self._db.commit()

        return tokens

    def refresh(self, refresh_token_value: str) -> TokenResponse:
        payload = self._decode_refresh_token(refresh_token_value)
        stored_token = self._repository.get_refresh_token(refresh_token_value)

        if stored_token is None:
            raise UnauthorizedError("Invalid refresh token")

        if stored_token.revoked_at is not None:
            raise UnauthorizedError("Refresh token has been revoked")

        if stored_token.expires_at < datetime.now(UTC):
            raise UnauthorizedError("Refresh token has expired")

        user = stored_token.user
        if user.status != UserStatus.ACTIVE:
            raise BusinessRuleViolationError("User account is not active")

        if str(user.id) != payload["sub"]:
            raise UnauthorizedError("Invalid refresh token")

        self._repository.revoke_refresh_token(stored_token)
        tokens = self._issue_tokens(user)

        self._activity_log.log_mutation(
            employee_id=user.employee.id if user.employee else None,
            user_id=user.id,
            action="TOKEN_REFRESH",
            entity="user",
            entity_id=user.id,
        )
        self._db.commit()
        return tokens

    def logout(self, user_id: UUID, refresh_token_value: str | None = None) -> None:
        user = self._repository.require_user(user_id)

        if refresh_token_value:
            stored_token = self._repository.get_refresh_token(refresh_token_value)
            if stored_token and stored_token.user_id == user.id:
                self._repository.revoke_refresh_token(stored_token)
        else:
            self._repository.revoke_all_user_tokens(user.id)

        self._activity_log.log_mutation(
            employee_id=user.employee.id if user.employee else None,
            user_id=user.id,
            action="LOGOUT",
            entity="user",
            entity_id=user.id,
        )
        publish_user_logged_out({"user_id": str(user.id), "email": user.email})
        self._db.commit()

    def get_current_user(self, user_id: UUID) -> UserResponse:
        user = self._repository.require_user(user_id)
        return self._build_user_response(user)

    def get_session(self, authenticated_user: AuthenticatedUser) -> SessionResponse:
        user = self._repository.require_user(authenticated_user.id)
        user_response = self._build_user_response(user)
        session = SessionInfo(
            user_id=authenticated_user.id,
            email=authenticated_user.email,
            roles=[role.value for role in authenticated_user.role_names],
            permissions=authenticated_user.permission_codes,
            is_active=authenticated_user.status == UserStatus.ACTIVE,
        )
        return SessionResponse(session=session, user=user_response)

    def build_authenticated_user(self, user: User) -> AuthenticatedUser:
        role_names = [UserRoleName(role.name) for role in user.roles]
        permission_codes = sorted(
            {permission.code for role in user.roles for permission in role.permissions}
        )
        return AuthenticatedUser(
            id=user.id,
            email=user.email,
            status=user.status,
            role_names=role_names,
            permission_codes=permission_codes,
            employee_id=user.employee.id if user.employee else None,
        )

    def require_permission(self, user: AuthenticatedUser, permission: PermissionCode) -> None:
        if not user.has_permission(permission.value):
            from app.shared.exceptions.base import PermissionDeniedError

            raise PermissionDeniedError(
                f"Missing required permission: {permission.value}",
            )

    def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        self._repository.save_refresh_token(user.id, refresh_token, expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=self._build_user_response(user),
        )

    def _build_user_response(self, user: User) -> UserResponse:
        permissions = sorted(
            {permission.code for role in user.roles for permission in role.permissions}
        )
        employee = None
        if user.employee:
            employee = EmployeeSummary.model_validate(user.employee)

        return UserResponse(
            id=user.id,
            email=user.email,
            status=user.status,
            last_login=user.last_login,
            roles=[RoleResponse.model_validate(role) for role in user.roles],
            permissions=permissions,
            employee=employee,
        )

    def _decode_refresh_token(self, token: str) -> dict:
        try:
            payload = decode_token(token)
        except ValueError as exc:
            raise UnauthorizedError("Invalid refresh token") from exc

        if payload.get("type") != "refresh":
            raise ValidationError("Token is not a refresh token")

        return payload
