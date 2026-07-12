"""Social module RBAC permissions."""

from app.auth.permissions import PermissionCode

READ_PERMISSION = PermissionCode.CSR_READ
WRITE_PERMISSION = PermissionCode.CSR_WRITE
PARTICIPATE_PERMISSION = PermissionCode.CSR_PARTICIPATE
