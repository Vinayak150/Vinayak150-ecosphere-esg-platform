from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.auth.middleware import rbac_permissions
from app.auth.schemas import AuthenticatedUser
from app.core.database import get_db
from app.modules.gamification.permissions import (
    PARTICIPATE_PERMISSION,
    READ_PERMISSION,
    WRITE_PERMISSION,
)
from app.modules.gamification.schemas import (
    BadgeCreate,
    BadgeUpdate,
    ChallengeCreate,
    ChallengeUpdate,
    GamificationListParams,
    ParticipationCreate,
    ParticipationRejectionRequest,
    ParticipationSubmit,
    RewardCreate,
    RewardRedemptionRequest,
    RewardUpdate,
)
from app.modules.gamification.service import GamificationService
from app.shared.utils.responses import success_response

router = APIRouter(prefix="/gamification", tags=["Gamification"])


def get_gamification_service(db: Session = Depends(get_db)) -> GamificationService:
    return GamificationService(db)


def get_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    category: str | None = Query(None),
    difficulty: str | None = Query(None),
    challenge_id: UUID | None = Query(None),
    employee_id: UUID | None = Query(None),
    approval_status: str | None = Query(None),
    department_id: UUID | None = Query(None),
) -> GamificationListParams:
    return GamificationListParams(
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
        status=status,
        category=category,
        difficulty=difficulty,
        challenge_id=challenge_id,
        employee_id=employee_id,
        approval_status=approval_status,
        department_id=department_id,
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
    service: Annotated[GamificationService, Depends(get_gamification_service)],
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
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    employees = service.list_employees()
    return success_response(
        request,
        message="Employees retrieved successfully",
        data=[employee.model_dump(mode="json") for employee in employees],
    )


@router.get(
    "/challenges",
    response_model=dict,
    summary="List challenges",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_challenges(
    request: Request,
    params: Annotated[GamificationListParams, Depends(get_list_params)],
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_challenges(params)
    return success_response(
        request,
        message="Challenges retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/challenges/{challenge_id}",
    response_model=dict,
    summary="Get challenge",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_challenge(
    request: Request,
    challenge_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    challenge = service.get_challenge(challenge_id)
    return success_response(
        request,
        message="Challenge retrieved successfully",
        data=challenge.model_dump(mode="json"),
    )


@router.post(
    "/challenges",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create challenge",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_challenge(
    request: Request,
    payload: ChallengeCreate,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    challenge = service.create_challenge(payload, current_user)
    return success_response(
        request,
        message="Challenge created successfully",
        data=challenge.model_dump(mode="json"),
    )


@router.put(
    "/challenges/{challenge_id}",
    response_model=dict,
    summary="Update challenge",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_challenge(
    request: Request,
    challenge_id: UUID,
    payload: ChallengeUpdate,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    challenge = service.update_challenge(challenge_id, payload, current_user)
    return success_response(
        request,
        message="Challenge updated successfully",
        data=challenge.model_dump(mode="json"),
    )


@router.delete(
    "/challenges/{challenge_id}",
    response_model=dict,
    summary="Delete challenge",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_challenge(
    request: Request,
    challenge_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_challenge(challenge_id, current_user)
    return success_response(request, message="Challenge deleted successfully", data=None)


@router.get(
    "/participation",
    response_model=dict,
    summary="List challenge participations",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_participations(
    request: Request,
    params: Annotated[GamificationListParams, Depends(get_list_params)],
    service: Annotated[GamificationService, Depends(get_gamification_service)],
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
    service: Annotated[GamificationService, Depends(get_gamification_service)],
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
    summary="Join challenge",
    dependencies=[Depends(require_permission(PARTICIPATE_PERMISSION.value))],
)
@rbac_permissions(PARTICIPATE_PERMISSION)
def join_challenge(
    request: Request,
    payload: ParticipationCreate,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    participation = service.join_challenge(payload, current_user)
    return success_response(
        request,
        message="Challenge joined successfully",
        data=participation.model_dump(mode="json"),
    )


@router.put(
    "/participation/{participation_id}",
    response_model=dict,
    summary="Submit challenge participation",
    dependencies=[Depends(require_permission(PARTICIPATE_PERMISSION.value))],
)
@rbac_permissions(PARTICIPATE_PERMISSION)
def submit_participation(
    request: Request,
    participation_id: UUID,
    payload: ParticipationSubmit,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    participation = service.submit_participation(participation_id, payload, current_user)
    return success_response(
        request,
        message="Participation submitted successfully",
        data=participation.model_dump(mode="json"),
    )


@router.post(
    "/participation/{participation_id}/approve",
    response_model=dict,
    summary="Approve challenge participation",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def approve_participation(
    request: Request,
    participation_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
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
    summary="Reject challenge participation",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def reject_participation(
    request: Request,
    participation_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    payload: ParticipationRejectionRequest | None = None,
) -> dict:
    participation = service.reject_participation(participation_id, current_user, payload)
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
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_participation(participation_id, current_user)
    return success_response(request, message="Participation deleted successfully", data=None)


@router.get(
    "/badges",
    response_model=dict,
    summary="List badges",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_badges(
    request: Request,
    params: Annotated[GamificationListParams, Depends(get_list_params)],
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_badges(params)
    return success_response(
        request,
        message="Badges retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/badges/{badge_id}",
    response_model=dict,
    summary="Get badge",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_badge(
    request: Request,
    badge_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    badge = service.get_badge(badge_id)
    return success_response(
        request,
        message="Badge retrieved successfully",
        data=badge.model_dump(mode="json"),
    )


@router.post(
    "/badges",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create badge",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_badge(
    request: Request,
    payload: BadgeCreate,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    badge = service.create_badge(payload, current_user)
    return success_response(
        request,
        message="Badge created successfully",
        data=badge.model_dump(mode="json"),
    )


@router.put(
    "/badges/{badge_id}",
    response_model=dict,
    summary="Update badge",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_badge(
    request: Request,
    badge_id: UUID,
    payload: BadgeUpdate,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    badge = service.update_badge(badge_id, payload, current_user)
    return success_response(
        request,
        message="Badge updated successfully",
        data=badge.model_dump(mode="json"),
    )


@router.delete(
    "/badges/{badge_id}",
    response_model=dict,
    summary="Delete badge",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_badge(
    request: Request,
    badge_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_badge(badge_id, current_user)
    return success_response(request, message="Badge deleted successfully", data=None)


@router.get(
    "/employee-badges",
    response_model=dict,
    summary="List employee badges",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_employee_badges(
    request: Request,
    params: Annotated[GamificationListParams, Depends(get_list_params)],
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_employee_badges(params)
    return success_response(
        request,
        message="Employee badges retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/rewards",
    response_model=dict,
    summary="List rewards",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_rewards(
    request: Request,
    params: Annotated[GamificationListParams, Depends(get_list_params)],
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_rewards(params)
    return success_response(
        request,
        message="Rewards retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/rewards/{reward_id}",
    response_model=dict,
    summary="Get reward",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_reward(
    request: Request,
    reward_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    reward = service.get_reward(reward_id)
    return success_response(
        request,
        message="Reward retrieved successfully",
        data=reward.model_dump(mode="json"),
    )


@router.post(
    "/rewards",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create reward",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def create_reward(
    request: Request,
    payload: RewardCreate,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    reward = service.create_reward(payload, current_user)
    return success_response(
        request,
        message="Reward created successfully",
        data=reward.model_dump(mode="json"),
    )


@router.put(
    "/rewards/{reward_id}",
    response_model=dict,
    summary="Update reward",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def update_reward(
    request: Request,
    reward_id: UUID,
    payload: RewardUpdate,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    reward = service.update_reward(reward_id, payload, current_user)
    return success_response(
        request,
        message="Reward updated successfully",
        data=reward.model_dump(mode="json"),
    )


@router.delete(
    "/rewards/{reward_id}",
    response_model=dict,
    summary="Delete reward",
    dependencies=[Depends(require_permission(WRITE_PERMISSION.value))],
)
@rbac_permissions(WRITE_PERMISSION)
def delete_reward(
    request: Request,
    reward_id: UUID,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    service.delete_reward(reward_id, current_user)
    return success_response(request, message="Reward deleted successfully", data=None)


@router.post(
    "/rewards/redeem",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Redeem reward",
    dependencies=[Depends(require_permission(PARTICIPATE_PERMISSION.value))],
)
@rbac_permissions(PARTICIPATE_PERMISSION)
def redeem_reward(
    request: Request,
    payload: RewardRedemptionRequest,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    redemption = service.redeem_reward(payload, current_user)
    return success_response(
        request,
        message="Reward redeemed successfully",
        data=redemption.model_dump(mode="json"),
    )


@router.get(
    "/redemptions",
    response_model=dict,
    summary="List reward redemptions",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def list_redemptions(
    request: Request,
    params: Annotated[GamificationListParams, Depends(get_list_params)],
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    items, pagination = service.list_redemptions(params)
    return success_response(
        request,
        message="Redemptions retrieved successfully",
        data={
            "data": [item.model_dump(mode="json") for item in items],
            "pagination": pagination,
        },
    )


@router.get(
    "/leaderboard/company",
    response_model=dict,
    summary="Company leaderboard",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_company_leaderboard(
    request: Request,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    leaderboard = service.get_company_leaderboard(limit=limit)
    return success_response(
        request,
        message="Company leaderboard retrieved successfully",
        data=[entry.model_dump(mode="json") for entry in leaderboard],
    )


@router.get(
    "/leaderboard/department",
    response_model=dict,
    summary="Department leaderboard",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_department_leaderboard(
    request: Request,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    leaderboard = service.get_department_leaderboard(limit=limit)
    return success_response(
        request,
        message="Department leaderboard retrieved successfully",
        data=[entry.model_dump(mode="json") for entry in leaderboard],
    )


@router.get(
    "/analytics/dashboard",
    response_model=dict,
    summary="Gamification analytics dashboard",
    dependencies=[Depends(require_permission(READ_PERMISSION.value))],
)
@rbac_permissions(READ_PERMISSION)
def get_analytics_dashboard(
    request: Request,
    service: Annotated[GamificationService, Depends(get_gamification_service)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    analytics = service.get_analytics()
    return success_response(
        request,
        message="Gamification analytics retrieved successfully",
        data=analytics.model_dump(mode="json"),
    )
