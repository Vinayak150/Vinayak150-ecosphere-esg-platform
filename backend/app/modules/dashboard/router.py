from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.auth.middleware import rbac_permissions
from app.auth.schemas import AuthenticatedUser
from app.core.database import get_db
from app.modules.dashboard.permissions import READ_PERMISSION
from app.modules.dashboard.service import DashboardService
from app.shared.utils.responses import success_response

router = APIRouter(tags=["Dashboard"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@router.get(
    "/dashboard",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get enterprise dashboard",
    description="Aggregated executive dashboard data from environmental and platform sources.",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_dashboard(
    request: Request,
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    dashboard = service.get_dashboard(current_user)
    return success_response(
        request,
        message="Dashboard data retrieved successfully",
        data=dashboard.model_dump(mode="json", by_alias=True),
    )
