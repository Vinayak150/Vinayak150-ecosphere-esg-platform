from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.auth.middleware import rbac_permissions
from app.auth.schemas import AuthenticatedUser
from app.core.database import get_db
from app.modules.social.permissions import (
    PARTICIPATE_PERMISSION,
    READ_PERMISSION,
    WRITE_PERMISSION,
)
from app.modules.social.schemas import (
    CsrActivityCreate,
    CsrActivityUpdate,
    ParticipationCreate,
    ParticipationRejectionRequest,
    ParticipationUpdate,
    SocialListParams,
)
from app.modules.social.service import SocialService
from app.shared.utils.responses import success_response

router = APIRouter(prefix="/social", tags=["Social"])


def get_social_service(db: Session = Depends(get_db)) -> SocialService:
    return SocialService(db)


def get_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    department_id: UUID | None = Query(None),
    category: str | None = Query(None),
    approval_status: str | None = Query(None),
    csr_activity_id: UUID | None = Query(None),
    employee_id: UUID | None = Query(None),
) -> SocialListParams:
    return SocialListParams(
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
        status=status,
        department_id=department_id,
        category=category,
        approval_status=approval_status,
        csr_activity_id=csr_activity_id,
        employee_id=employee_id,
    )


@router.get(
    "/departments",
    response_model=dict,
    summary="List departments",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_departments(
    request: Request,
    service: Annotated[SocialService, Depends(get_social_service)],
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
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_employees(
    request: Request,
    service: Annotated[SocialService, Depends(get_social_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    employees = service.list_employees()
    return success_response(
        request,
        message="Employees retrieved successfully",
        data=[employee.model_dump(mode="json") for employee in employees],
    )


@router.get(
    "/csr-activities",
    response_model=dict,
    summary="List CSR activities",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_csr_activities(
    request: Request,
    params: Annotated[SocialListParams, Depends(get_list_params)],
    service: Annotated[SocialService, Depends(get_social_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_csr_activities(params)
    return success_response(
        request,
        message="CSR activities retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/csr-activities/{activity_id}",
    response_model=dict,
    summary="Get CSR activity",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_csr_activity(
    request: Request,
    activity_id: UUID,
    service: Annotated[SocialService, Depends(get_social_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    activity = service.get_csr_activity(activity_id)
    return success_response(
        request,
        message="CSR activity retrieved successfully",
        data=activity.model_dump(mode="json"),
    )


@router.post(
    "/csr-activities",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create CSR activity",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_csr_activity(
    request: Request,
    payload: CsrActivityCreate,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    activity = service.create_csr_activity(payload, current_user)
    return success_response(
        request,
        message="CSR activity created successfully",
        data=activity.model_dump(mode="json"),
    )


@router.put(
    "/csr-activities/{activity_id}",
    response_model=dict,
    summary="Update CSR activity",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_csr_activity(
    request: Request,
    activity_id: UUID,
    payload: CsrActivityUpdate,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    activity = service.update_csr_activity(activity_id, payload, current_user)
    return success_response(
        request,
        message="CSR activity updated successfully",
        data=activity.model_dump(mode="json"),
    )


@router.delete(
    "/csr-activities/{activity_id}",
    response_model=dict,
    summary="Delete CSR activity",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_csr_activity(
    request: Request,
    activity_id: UUID,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_csr_activity(activity_id, current_user)
    return success_response(request, message="CSR activity deleted successfully")


@router.get(
    "/participation",
    response_model=dict,
    summary="List employee participations",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_participations(
    request: Request,
    params: Annotated[SocialListParams, Depends(get_list_params)],
    service: Annotated[SocialService, Depends(get_social_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_participations(params)
    return success_response(
        request,
        message="Participations retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/participation/{participation_id}",
    response_model=dict,
    summary="Get participation",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_participation(
    request: Request,
    participation_id: UUID,
    service: Annotated[SocialService, Depends(get_social_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    participation = service.get_participation(participation_id)
    return success_response(
        request,
        message="Participation retrieved successfully",
        data=participation.model_dump(mode="json"),
    )


@router.post(
    "/participation",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Join CSR activity",
    dependencies=[Depends(require_permission(PARTICIPATE_PERMISSION.value))],
)
@rbac_permissions(PARTICIPATE_PERMISSION)
def create_participation(
    request: Request,
    payload: ParticipationCreate,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    participation = service.create_participation(payload, current_user)
    return success_response(
        request,
        message="Participation created successfully",
        data=participation.model_dump(mode="json"),
    )


@router.put(
    "/participation/{participation_id}",
    response_model=dict,
    summary="Update participation proof",
    dependencies=[Depends(require_permission(PARTICIPATE_PERMISSION.value))],
)
@rbac_permissions(PARTICIPATE_PERMISSION)
def update_participation(
    request: Request,
    participation_id: UUID,
    payload: ParticipationUpdate,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    participation = service.update_participation(participation_id, payload, current_user)
    return success_response(
        request,
        message="Participation updated successfully",
        data=participation.model_dump(mode="json"),
    )


@router.post(
    "/participation/{participation_id}/approve",
    response_model=dict,
    summary="Approve participation",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def approve_participation(
    request: Request,
    participation_id: UUID,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    participation = service.approve_participation(participation_id, current_user)
    return success_response(
        request,
        message="Participation approved successfully",
        data=participation.model_dump(mode="json"),
    )


@router.post(
    "/participation/{participation_id}/reject",
    response_model=dict,
    summary="Reject participation",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def reject_participation(
    request: Request,
    participation_id: UUID,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    payload: ParticipationRejectionRequest | None = None,
) -> dict:
    reason = payload.rejection_reason if payload else None
    participation = service.reject_participation(participation_id, current_user, reason)
    return success_response(
        request,
        message="Participation rejected successfully",
        data=participation.model_dump(mode="json"),
    )


@router.delete(
    "/participation/{participation_id}",
    response_model=dict,
    summary="Delete participation",
    dependencies=[Depends(require_permission(PARTICIPATE_PERMISSION.value))],
)
@rbac_permissions(PARTICIPATE_PERMISSION)
def delete_participation(
    request: Request,
    participation_id: UUID,
    service: Annotated[SocialService, Depends(get_social_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_participation(participation_id, current_user)
    return success_response(request, message="Participation deleted successfully")


@router.get(
    "/analytics/dashboard",
    response_model=dict,
    summary="Social analytics dashboard",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_social_analytics(
    request: Request,
    service: Annotated[SocialService, Depends(get_social_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    analytics = service.get_analytics()
    return success_response(
        request,
        message="Social analytics retrieved successfully",
        data=analytics.model_dump(mode="json"),
    )
