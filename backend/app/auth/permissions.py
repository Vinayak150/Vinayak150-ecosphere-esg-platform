"""RBAC permission definitions aligned with the authorization matrix."""

from enum import StrEnum


class PermissionCode(StrEnum):
    DASHBOARD_READ = "dashboard:read"
    DEPARTMENTS_READ = "departments:read"
    DEPARTMENTS_WRITE = "departments:write"
    CARBON_READ = "carbon:read"
    CARBON_WRITE = "carbon:write"
    CSR_READ = "csr:read"
    CSR_WRITE = "csr:write"
    CSR_PARTICIPATE = "csr:participate"
    POLICIES_READ = "policies:read"
    POLICIES_WRITE = "policies:write"
    POLICIES_ACKNOWLEDGE = "policies:acknowledge"
    AUDITS_READ = "audits:read"
    AUDITS_WRITE = "audits:write"
    CHALLENGES_READ = "challenges:read"
    CHALLENGES_WRITE = "challenges:write"
    CHALLENGES_PARTICIPATE = "challenges:participate"
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"


ROLE_PERMISSIONS: dict[str, list[PermissionCode]] = {
    "ADMIN": list(PermissionCode),
    "ESG_MANAGER": [
        PermissionCode.DASHBOARD_READ,
        PermissionCode.CARBON_READ,
        PermissionCode.CARBON_WRITE,
        PermissionCode.CSR_READ,
        PermissionCode.CSR_WRITE,
        PermissionCode.POLICIES_READ,
        PermissionCode.POLICIES_WRITE,
        PermissionCode.AUDITS_READ,
        PermissionCode.AUDITS_WRITE,
        PermissionCode.CHALLENGES_READ,
        PermissionCode.CHALLENGES_WRITE,
        PermissionCode.REPORTS_READ,
        PermissionCode.REPORTS_EXPORT,
        PermissionCode.SETTINGS_READ,
    ],
    "HR_MANAGER": [
        PermissionCode.DASHBOARD_READ,
        PermissionCode.CSR_READ,
        PermissionCode.CSR_WRITE,
        PermissionCode.CHALLENGES_READ,
        PermissionCode.CHALLENGES_WRITE,
        PermissionCode.REPORTS_READ,
        PermissionCode.SETTINGS_READ,
    ],
    "AUDITOR": [
        PermissionCode.DASHBOARD_READ,
        PermissionCode.POLICIES_READ,
        PermissionCode.AUDITS_READ,
        PermissionCode.REPORTS_READ,
        PermissionCode.REPORTS_EXPORT,
    ],
    "EMPLOYEE": [
        PermissionCode.DASHBOARD_READ,
        PermissionCode.CARBON_READ,
        PermissionCode.CSR_PARTICIPATE,
        PermissionCode.POLICIES_READ,
        PermissionCode.POLICIES_ACKNOWLEDGE,
        PermissionCode.AUDITS_READ,
        PermissionCode.CHALLENGES_PARTICIPATE,
        PermissionCode.REPORTS_READ,
    ],
}
