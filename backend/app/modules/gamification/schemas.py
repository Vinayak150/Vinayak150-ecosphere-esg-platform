from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.gamification.models import (
    BadgeStatus,
    ChallengeDifficulty,
    ChallengeStatus,
    ParticipationApproval,
    RewardStatus,
)
from app.shared.schemas.responses import PaginationParams


class GamificationListParams(PaginationParams):
    status: str | None = None
    category: str | None = None
    difficulty: str | None = None
    challenge_id: UUID | None = None
    employee_id: UUID | None = None
    approval_status: str | None = None
    department_id: UUID | None = None


class ChallengeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = None
    xp: int = Field(default=0, ge=0)
    difficulty: ChallengeDifficulty = ChallengeDifficulty.MEDIUM
    evidence_required: bool = False
    deadline: date
    status: ChallengeStatus = ChallengeStatus.DRAFT


class ChallengeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    xp: int | None = Field(default=None, ge=0)
    difficulty: ChallengeDifficulty | None = None
    evidence_required: bool | None = None
    deadline: date | None = None
    status: ChallengeStatus | None = None


class ChallengeResponse(BaseModel):
    id: UUID
    title: str
    category: str
    description: str | None
    xp: int
    difficulty: ChallengeDifficulty
    evidence_required: bool
    deadline: date
    status: ChallengeStatus
    participation_count: int = 0
    approved_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParticipationCreate(BaseModel):
    challenge_id: UUID


class ParticipationSubmit(BaseModel):
    progress: int = Field(default=100, ge=0, le=100)
    proof_file: str | None = Field(default=None, max_length=500)


class ParticipationRejectionRequest(BaseModel):
    rejection_reason: str | None = Field(default=None, max_length=500)


class ParticipationResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: str | None = None
    department_name: str | None = None
    challenge_id: UUID
    challenge_title: str | None = None
    progress: int
    proof_file: str | None
    approval_status: ParticipationApproval
    xp_awarded: int
    completion_date: date | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BadgeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    unlock_rule: dict = Field(default_factory=dict)
    icon: str | None = Field(default=None, max_length=255)
    status: BadgeStatus = BadgeStatus.ACTIVE


class BadgeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    unlock_rule: dict | None = None
    icon: str | None = Field(default=None, max_length=255)
    status: BadgeStatus | None = None


class BadgeResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    unlock_rule: dict
    icon: str | None
    status: BadgeStatus
    earned_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeBadgeResponse(BaseModel):
    id: UUID
    badge_id: UUID
    badge_name: str | None = None
    badge_icon: str | None = None
    employee_id: UUID
    employee_name: str | None = None
    earned_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RewardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    points_required: int = Field(ge=1)
    stock: int = Field(default=0, ge=0)
    status: RewardStatus = RewardStatus.ACTIVE


class RewardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    points_required: int | None = Field(default=None, ge=1)
    stock: int | None = Field(default=None, ge=0)
    status: RewardStatus | None = None


class RewardResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    points_required: int
    stock: int
    status: RewardStatus
    redemption_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RewardRedemptionRequest(BaseModel):
    reward_id: UUID


class RewardRedemptionResponse(BaseModel):
    id: UUID
    reward_id: UUID
    reward_name: str | None = None
    employee_id: UUID
    employee_name: str | None = None
    redeemed_points: int
    redeemed_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    employee_id: UUID
    employee_name: str
    department_id: UUID | None = None
    department_name: str | None = None
    total_xp: int
    badge_count: int = 0


class DepartmentLeaderboardEntry(BaseModel):
    rank: int
    department_id: UUID
    department_name: str
    total_xp: int
    employee_count: int
    average_xp: Decimal


class BadgeDistributionItem(BaseModel):
    badge_id: UUID
    badge_name: str
    earned_count: int


class GamificationAnalyticsResponse(BaseModel):
    total_xp: int
    total_challenges: int
    active_challenges: int
    completed_challenges: int
    challenge_completion_rate: Decimal
    total_badges: int
    total_badge_awards: int
    badge_distribution: list[BadgeDistributionItem]
    top_employees: list[LeaderboardEntry]
    top_departments: list[DepartmentLeaderboardEntry]
    pending_reviews: int


class EmployeeOption(BaseModel):
    id: UUID
    name: str
    email: str
    department_name: str | None = None
    total_xp: int = 0
