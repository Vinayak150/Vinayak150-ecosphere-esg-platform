import hashlib
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.auth.models import RefreshToken, Role, User, UserRoleName
from app.shared.exceptions.base import NotFoundError


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_user_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .options(
                joinedload(User.roles).joinedload(Role.permissions),
                joinedload(User.employee),
            )
            .where(User.email == email)
        )
        return self._db.scalars(stmt).unique().first()

    def get_user_by_id(self, user_id: UUID) -> User | None:
        stmt = (
            select(User)
            .options(
                joinedload(User.roles).joinedload(Role.permissions),
                joinedload(User.employee),
            )
            .where(User.id == user_id)
        )
        return self._db.scalars(stmt).unique().first()

    def get_role_by_name(self, name: UserRoleName) -> Role | None:
        stmt = select(Role).where(Role.name == name.value)
        return self._db.scalars(stmt).first()

    def update_last_login(self, user: User) -> None:
        user.last_login = datetime.now(UTC)
        self._db.add(user)
        self._db.flush()

    def save_refresh_token(self, user_id: UUID, token: str, expires_at: datetime) -> RefreshToken:
        token_hash = self._hash_token(token)
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._db.add(refresh_token)
        self._db.flush()
        return refresh_token

    def get_refresh_token(self, token: str) -> RefreshToken | None:
        token_hash = self._hash_token(token)
        stmt = (
            select(RefreshToken)
            .options(
                joinedload(RefreshToken.user).joinedload(User.roles).joinedload(Role.permissions)
            )
            .where(RefreshToken.token_hash == token_hash)
        )
        return self._db.scalars(stmt).unique().first()

    def revoke_refresh_token(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(UTC)
        self._db.add(refresh_token)
        self._db.flush()

    def revoke_all_user_tokens(self, user_id: UUID) -> None:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        tokens = self._db.scalars(stmt).all()
        now = datetime.now(UTC)
        for token in tokens:
            token.revoked_at = now
            self._db.add(token)
        self._db.flush()

    def require_user(self, user_id: UUID) -> User:
        user = self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
