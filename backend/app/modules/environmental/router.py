from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.auth.middleware import rbac_permissions
from app.auth.schemas import AuthenticatedUser
from app.core.database import get_db
from app.modules.environmental.permissions import READ_PERMISSION, WRITE_PERMISSION
from app.modules.environmental.schemas import (
    CarbonCalculationRequest,
    CarbonTransactionCreate,
    CarbonTransactionUpdate,
    EmissionFactorCreate,
    EmissionFactorUpdate,
    EnvironmentalGoalCreate,
    EnvironmentalGoalUpdate,
    EnvironmentalListParams,
    ProductEsgCreate,
    ProductEsgUpdate,
)
from app.modules.environmental.service import EnvironmentalService
from app.shared.utils.responses import success_response

router = APIRouter(prefix="/environmental", tags=["Environmental"])


def get_environmental_service(db: Session = Depends(get_db)) -> EnvironmentalService:
    return EnvironmentalService(db)


def get_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    department_id: UUID | None = Query(None),
    source_type: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
) -> EnvironmentalListParams:
    return EnvironmentalListParams(
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
        status=status,
        department_id=department_id,
        source_type=source_type,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/departments",
    response_model=dict,
    summary="List departments",
    description="Return active departments for environmental data entry.",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_departments(
    request: Request,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    departments = service.list_departments()
    return success_response(
        request,
        message="Departments retrieved successfully",
        data=departments,
    )


@router.get(
    "/emission-factors",
    response_model=dict,
    summary="List emission factors",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_emission_factors(
    request: Request,
    params: Annotated[EnvironmentalListParams, Depends(get_list_params)],
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_emission_factors(params)
    return success_response(
        request,
        message="Emission factors retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/emission-factors/{factor_id}",
    response_model=dict,
    summary="Get emission factor",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_emission_factor(
    request: Request,
    factor_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    factor = service.get_emission_factor(factor_id)
    return success_response(
        request,
        message="Emission factor retrieved successfully",
        data=factor.model_dump(mode="json"),
    )


@router.post(
    "/emission-factors",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create emission factor",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_emission_factor(
    request: Request,
    payload: EmissionFactorCreate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    factor = service.create_emission_factor(payload, current_user)
    return success_response(
        request,
        message="Emission factor created successfully",
        data=factor.model_dump(mode="json"),
    )


@router.put(
    "/emission-factors/{factor_id}",
    response_model=dict,
    summary="Update emission factor",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_emission_factor(
    request: Request,
    factor_id: UUID,
    payload: EmissionFactorUpdate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    factor = service.update_emission_factor(factor_id, payload, current_user)
    return success_response(
        request,
        message="Emission factor updated successfully",
        data=factor.model_dump(mode="json"),
    )


@router.delete(
    "/emission-factors/{factor_id}",
    response_model=dict,
    summary="Delete emission factor",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_emission_factor(
    request: Request,
    factor_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_emission_factor(factor_id, current_user)
    return success_response(request, message="Emission factor deleted successfully")


@router.get(
    "/carbon-transactions",
    response_model=dict,
    summary="List carbon transactions",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_carbon_transactions(
    request: Request,
    params: Annotated[EnvironmentalListParams, Depends(get_list_params)],
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_carbon_transactions(params)
    return success_response(
        request,
        message="Carbon transactions retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.post(
    "/carbon-transactions/calculate",
    response_model=dict,
    summary="Calculate carbon emissions",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def calculate_carbon(
    request: Request,
    payload: CarbonCalculationRequest,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    result = service.calculate_carbon(payload)
    return success_response(
        request,
        message="Carbon emission calculated successfully",
        data=result.model_dump(mode="json"),
    )


@router.get(
    "/carbon-transactions/{transaction_id}",
    response_model=dict,
    summary="Get carbon transaction",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_carbon_transaction(
    request: Request,
    transaction_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    transaction = service.get_carbon_transaction(transaction_id)
    return success_response(
        request,
        message="Carbon transaction retrieved successfully",
        data=transaction.model_dump(mode="json"),
    )


@router.post(
    "/carbon-transactions",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create carbon transaction",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_carbon_transaction(
    request: Request,
    payload: CarbonTransactionCreate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    transaction = service.create_carbon_transaction(payload, current_user)
    return success_response(
        request,
        message="Carbon transaction created successfully",
        data=transaction.model_dump(mode="json"),
    )


@router.put(
    "/carbon-transactions/{transaction_id}",
    response_model=dict,
    summary="Update carbon transaction",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_carbon_transaction(
    request: Request,
    transaction_id: UUID,
    payload: CarbonTransactionUpdate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    transaction = service.update_carbon_transaction(transaction_id, payload, current_user)
    return success_response(
        request,
        message="Carbon transaction updated successfully",
        data=transaction.model_dump(mode="json"),
    )


@router.delete(
    "/carbon-transactions/{transaction_id}",
    response_model=dict,
    summary="Delete carbon transaction",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_carbon_transaction(
    request: Request,
    transaction_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_carbon_transaction(transaction_id, current_user)
    return success_response(request, message="Carbon transaction deleted successfully")


@router.get(
    "/goals",
    response_model=dict,
    summary="List environmental goals",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_environmental_goals(
    request: Request,
    params: Annotated[EnvironmentalListParams, Depends(get_list_params)],
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_environmental_goals(params)
    return success_response(
        request,
        message="Environmental goals retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/goals/{goal_id}",
    response_model=dict,
    summary="Get environmental goal",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_environmental_goal(
    request: Request,
    goal_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    goal = service.get_environmental_goal(goal_id)
    return success_response(
        request,
        message="Environmental goal retrieved successfully",
        data=goal.model_dump(mode="json"),
    )


@router.post(
    "/goals",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create environmental goal",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_environmental_goal(
    request: Request,
    payload: EnvironmentalGoalCreate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    goal = service.create_environmental_goal(payload, current_user)
    return success_response(
        request,
        message="Environmental goal created successfully",
        data=goal.model_dump(mode="json"),
    )


@router.put(
    "/goals/{goal_id}",
    response_model=dict,
    summary="Update environmental goal",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_environmental_goal(
    request: Request,
    goal_id: UUID,
    payload: EnvironmentalGoalUpdate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    goal = service.update_environmental_goal(goal_id, payload, current_user)
    return success_response(
        request,
        message="Environmental goal updated successfully",
        data=goal.model_dump(mode="json"),
    )


@router.delete(
    "/goals/{goal_id}",
    response_model=dict,
    summary="Delete environmental goal",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_environmental_goal(
    request: Request,
    goal_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_environmental_goal(goal_id, current_user)
    return success_response(request, message="Environmental goal deleted successfully")


@router.get(
    "/product-esg-profiles",
    response_model=dict,
    summary="List product ESG profiles",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_product_esg_profiles(
    request: Request,
    params: Annotated[EnvironmentalListParams, Depends(get_list_params)],
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_product_esg_profiles(params)
    return success_response(
        request,
        message="Product ESG profiles retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/product-esg-profiles/{profile_id}",
    response_model=dict,
    summary="Get product ESG profile",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_product_esg_profile(
    request: Request,
    profile_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    profile = service.get_product_esg_profile(profile_id)
    return success_response(
        request,
        message="Product ESG profile retrieved successfully",
        data=profile.model_dump(mode="json"),
    )


@router.post(
    "/product-esg-profiles",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create product ESG profile",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_product_esg_profile(
    request: Request,
    payload: ProductEsgCreate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    profile = service.create_product_esg_profile(payload, current_user)
    return success_response(
        request,
        message="Product ESG profile created successfully",
        data=profile.model_dump(mode="json"),
    )


@router.put(
    "/product-esg-profiles/{profile_id}",
    response_model=dict,
    summary="Update product ESG profile",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_product_esg_profile(
    request: Request,
    profile_id: UUID,
    payload: ProductEsgUpdate,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    profile = service.update_product_esg_profile(profile_id, payload, current_user)
    return success_response(
        request,
        message="Product ESG profile updated successfully",
        data=profile.model_dump(mode="json"),
    )


@router.delete(
    "/product-esg-profiles/{profile_id}",
    response_model=dict,
    summary="Delete product ESG profile",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_product_esg_profile(
    request: Request,
    profile_id: UUID,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_product_esg_profile(profile_id, current_user)
    return success_response(request, message="Product ESG profile deleted successfully")


@router.get(
    "/analytics/dashboard",
    response_model=dict,
    summary="Environmental analytics dashboard",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_environmental_analytics(
    request: Request,
    service: Annotated[EnvironmentalService, Depends(get_environmental_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    analytics = service.get_analytics()
    return success_response(
        request,
        message="Environmental analytics retrieved successfully",
        data=analytics.model_dump(mode="json"),
    )
