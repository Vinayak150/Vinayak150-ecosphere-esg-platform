"""Governance module RBAC permissions."""

from app.auth.permissions import PermissionCode

POLICIES_READ = PermissionCode.POLICIES_READ
POLICIES_WRITE = PermissionCode.POLICIES_WRITE
POLICIES_ACKNOWLEDGE = PermissionCode.POLICIES_ACKNOWLEDGE
AUDITS_READ = PermissionCode.AUDITS_READ
AUDITS_WRITE = PermissionCode.AUDITS_WRITE
