from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.auth.middleware import rbac_permissions
from app.auth.schemas import AuthenticatedUser
from app.core.database import get_db
from app.modules.governance.permissions import (
    AUDITS_READ,
    AUDITS_WRITE,
    POLICIES_ACKNOWLEDGE,
    POLICIES_READ,
    POLICIES_WRITE,
)
from app.modules.governance.schemas import (
    AuditCreate,
    AuditUpdate,
    ComplianceIssueCreate,
    ComplianceIssueUpdate,
    GovernanceListParams,
    PolicyAcknowledgementCreate,
    PolicyCreate,
    PolicyUpdate,
)
from app.modules.governance.service import GovernanceService
from app.shared.utils.responses import success_response

router = APIRouter(prefix="/governance", tags=["Governance"])


def get_governance_service(db: Session = Depends(get_db)) -> GovernanceService:
    return GovernanceService(db)


def get_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    department_id: UUID | None = Query(None),
    policy_id: UUID | None = Query(None),
    employee_id: UUID | None = Query(None),
    audit_id: UUID | None = Query(None),
    owner_id: UUID | None = Query(None),
    severity: str | None = Query(None),
) -> GovernanceListParams:
    return GovernanceListParams(
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
        status=status,
        department_id=department_id,
        policy_id=policy_id,
        employee_id=employee_id,
        audit_id=audit_id,
        owner_id=owner_id,
        severity=severity,
    )


@router.get(
    "/departments",
    response_model=dict,
    summary="List departments",
    dependencies=[Depends(require_permission(POLICIES_READ.value))],
)
@rbac_permissions(POLICIES_READ)
def list_departments(
    request: Request,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    departments = service.list_departments()
    return success_response(
        request,
        message="Departments retrieved successfully",
        data=departments,
    )


@router.get(
    "/employees",
    response_model=dict,
    summary="List employees",
    dependencies=[Depends(require_permission(POLICIES_READ.value))],
)
@rbac_permissions(POLICIES_READ)
def list_employees(
    request: Request,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    employees = service.list_employees()
    return success_response(
        request,
        message="Employees retrieved successfully",
        data=[employee.model_dump(mode="json") for employee in employees],
    )


@router.get(
    "/policies",
    response_model=dict,
    summary="List policies",
    dependencies=[Depends(require_permission(POLICIES_READ.value))],
)
@rbac_permissions(POLICIES_READ)
def list_policies(
    request: Request,
    params: Annotated[GovernanceListParams, Depends(get_list_params)],
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_policies(params)
    return success_response(
        request,
        message="Policies retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/policies/{policy_id}",
    response_model=dict,
    summary="Get policy",
    dependencies=[Depends(require_permission(POLICIES_READ.value))],
)
@rbac_permissions(POLICIES_READ)
def get_policy(
    request: Request,
    policy_id: UUID,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    policy = service.get_policy(policy_id)
    return success_response(
        request,
        message="Policy retrieved successfully",
        data=policy.model_dump(mode="json"),
    )


@router.post(
    "/policies",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create policy",
    dependencies=[Depends(require_permission(POLICIES_WRITE.value))],
)
@rbac_permissions(POLICIES_WRITE)
def create_policy(
    request: Request,
    payload: PolicyCreate,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    policy = service.create_policy(payload, current_user)
    return success_response(
        request,
        message="Policy created successfully",
        data=policy.model_dump(mode="json"),
    )


@router.put(
    "/policies/{policy_id}",
    response_model=dict,
    summary="Update policy",
    dependencies=[Depends(require_permission(POLICIES_WRITE.value))],
)
@rbac_permissions(POLICIES_WRITE)
def update_policy(
    request: Request,
    policy_id: UUID,
    payload: PolicyUpdate,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    policy = service.update_policy(policy_id, payload, current_user)
    return success_response(
        request,
        message="Policy updated successfully",
        data=policy.model_dump(mode="json"),
    )


@router.delete(
    "/policies/{policy_id}",
    response_model=dict,
    summary="Delete policy",
    dependencies=[Depends(require_permission(POLICIES_WRITE.value))],
)
@rbac_permissions(POLICIES_WRITE)
def delete_policy(
    request: Request,
    policy_id: UUID,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_policy(policy_id, current_user)
    return success_response(request, message="Policy deleted successfully")


@router.get(
    "/policy-acknowledgements",
    response_model=dict,
    summary="List policy acknowledgements",
    dependencies=[Depends(require_permission(POLICIES_READ.value))],
)
@rbac_permissions(POLICIES_READ)
def list_acknowledgements(
    request: Request,
    params: Annotated[GovernanceListParams, Depends(get_list_params)],
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_acknowledgements(params)
    return success_response(
        request,
        message="Policy acknowledgements retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.post(
    "/policy-acknowledgements",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Acknowledge policy",
    dependencies=[Depends(require_permission(POLICIES_ACKNOWLEDGE.value))],
)
@rbac_permissions(POLICIES_ACKNOWLEDGE)
def acknowledge_policy(
    request: Request,
    payload: PolicyAcknowledgementCreate,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    acknowledgement = service.acknowledge_policy(payload, current_user)
    return success_response(
        request,
        message="Policy acknowledged successfully",
        data=acknowledgement.model_dump(mode="json"),
    )


@router.get(
    "/audits",
    response_model=dict,
    summary="List audits",
    dependencies=[Depends(require_permission(AUDITS_READ.value))],
)
@rbac_permissions(AUDITS_READ)
def list_audits(
    request: Request,
    params: Annotated[GovernanceListParams, Depends(get_list_params)],
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_audits(params)
    return success_response(
        request,
        message="Audits retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/audits/{audit_id}",
    response_model=dict,
    summary="Get audit",
    dependencies=[Depends(require_permission(AUDITS_READ.value))],
)
@rbac_permissions(AUDITS_READ)
def get_audit(
    request: Request,
    audit_id: UUID,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    audit = service.get_audit(audit_id)
    return success_response(
        request,
        message="Audit retrieved successfully",
        data=audit.model_dump(mode="json"),
    )


@router.post(
    "/audits",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create audit",
    dependencies=[Depends(require_permission(AUDITS_WRITE.value))],
)
@rbac_permissions(AUDITS_WRITE)
def create_audit(
    request: Request,
    payload: AuditCreate,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    audit = service.create_audit(payload, current_user)
    return success_response(
        request,
        message="Audit created successfully",
        data=audit.model_dump(mode="json"),
    )


@router.put(
    "/audits/{audit_id}",
    response_model=dict,
    summary="Update audit",
    dependencies=[Depends(require_permission(AUDITS_WRITE.value))],
)
@rbac_permissions(AUDITS_WRITE)
def update_audit(
    request: Request,
    audit_id: UUID,
    payload: AuditUpdate,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    audit = service.update_audit(audit_id, payload, current_user)
    return success_response(
        request,
        message="Audit updated successfully",
        data=audit.model_dump(mode="json"),
    )


@router.delete(
    "/audits/{audit_id}",
    response_model=dict,
    summary="Delete audit",
    dependencies=[Depends(require_permission(AUDITS_WRITE.value))],
)
@rbac_permissions(AUDITS_WRITE)
def delete_audit(
    request: Request,
    audit_id: UUID,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_audit(audit_id, current_user)
    return success_response(request, message="Audit deleted successfully")


@router.get(
    "/compliance-issues",
    response_model=dict,
    summary="List compliance issues",
    dependencies=[Depends(require_permission(AUDITS_READ.value))],
)
@rbac_permissions(AUDITS_READ)
def list_compliance_issues(
    request: Request,
    params: Annotated[GovernanceListParams, Depends(get_list_params)],
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_compliance_issues(params)
    return success_response(
        request,
        message="Compliance issues retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/compliance-issues/{issue_id}",
    response_model=dict,
    summary="Get compliance issue",
    dependencies=[Depends(require_permission(AUDITS_READ.value))],
)
@rbac_permissions(AUDITS_READ)
def get_compliance_issue(
    request: Request,
    issue_id: UUID,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    issue = service.get_compliance_issue(issue_id)
    return success_response(
        request,
        message="Compliance issue retrieved successfully",
        data=issue.model_dump(mode="json"),
    )


@router.post(
    "/compliance-issues",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create compliance issue",
    dependencies=[Depends(require_permission(AUDITS_WRITE.value))],
)
@rbac_permissions(AUDITS_WRITE)
def create_compliance_issue(
    request: Request,
    payload: ComplianceIssueCreate,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    issue = service.create_compliance_issue(payload, current_user)
    return success_response(
        request,
        message="Compliance issue created successfully",
        data=issue.model_dump(mode="json"),
    )


@router.put(
    "/compliance-issues/{issue_id}",
    response_model=dict,
    summary="Update compliance issue",
    dependencies=[Depends(require_permission(AUDITS_WRITE.value))],
)
@rbac_permissions(AUDITS_WRITE)
def update_compliance_issue(
    request: Request,
    issue_id: UUID,
    payload: ComplianceIssueUpdate,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    issue = service.update_compliance_issue(issue_id, payload, current_user)
    return success_response(
        request,
        message="Compliance issue updated successfully",
        data=issue.model_dump(mode="json"),
    )


@router.post(
    "/compliance-issues/{issue_id}/close",
    response_model=dict,
    summary="Close compliance issue",
    dependencies=[Depends(require_permission(AUDITS_WRITE.value))],
)
@rbac_permissions(AUDITS_WRITE)
def close_compliance_issue(
    request: Request,
    issue_id: UUID,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    issue = service.close_compliance_issue(issue_id, current_user)
    return success_response(
        request,
        message="Compliance issue closed successfully",
        data=issue.model_dump(mode="json"),
    )


@router.delete(
    "/compliance-issues/{issue_id}",
    response_model=dict,
    summary="Delete compliance issue",
    dependencies=[Depends(require_permission(AUDITS_WRITE.value))],
)
@rbac_permissions(AUDITS_WRITE)
def delete_compliance_issue(
    request: Request,
    issue_id: UUID,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_compliance_issue(issue_id, current_user)
    return success_response(request, message="Compliance issue deleted successfully")


@router.get(
    "/analytics/dashboard",
    response_model=dict,
    summary="Governance analytics dashboard",
    dependencies=[Depends(require_permission(POLICIES_READ.value))],
)
@rbac_permissions(POLICIES_READ)
def get_governance_analytics(
    request: Request,
    service: Annotated[GovernanceService, Depends(get_governance_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    analytics = service.get_analytics()
    return success_response(
        request,
        message="Governance analytics retrieved successfully",
        data=analytics.model_dump(mode="json"),
    )
