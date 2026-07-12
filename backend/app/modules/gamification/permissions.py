"""Gamification module RBAC permissions."""

from app.auth.permissions import PermissionCode

READ_PERMISSION = PermissionCode.CHALLENGES_READ
WRITE_PERMISSION = PermissionCode.CHALLENGES_WRITE
PARTICIPATE_PERMISSION = PermissionCode.CHALLENGES_PARTICIPATE
