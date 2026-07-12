from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.environmental.schemas import (
    GoalProgressItem,
    MonthlyCarbonTrendPoint,
    TopCarbonSource,
)
from app.modules.gamification.schemas import (
    ChallengeResponse,
    EmployeeBadgeResponse,
    LeaderboardEntry,
)


class DepartmentRankingItem(BaseModel):
    rank: int
    department_id: UUID
    department_name: str
    environmental_score: Decimal
    total_emission: Decimal
    goals_completed: int
    goals_total: int


class RecentCarbonTransactionItem(BaseModel):
    id: UUID
    activity_name: str
    department_name: str | None
    emission_factor_name: str | None
    calculated_emission: Decimal
    transaction_date: date
    created_at: datetime


class RecentActivityItem(BaseModel):
    id: UUID
    action: str
    entity: str
    entity_id: UUID | None
    message: str
    created_at: datetime


class DashboardNotification(BaseModel):
    id: str
    type: str
    title: str
    message: str
    severity: str
    created_at: datetime
    read: bool = False


class QuickStatItem(BaseModel):
    key: str
    label: str
    value: str
    trend: str | None = None


class QuickActionItem(BaseModel):
    id: str
    label: str
    description: str
    route: str
    permission: str
    enabled: bool


class PillarScore(BaseModel):
    score: Decimal | None
    available: bool
    label: str


class DashboardResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    overall_esg: Decimal = Field(serialization_alias="overallESG")
    environmental_score: PillarScore = Field(serialization_alias="environmentalScore")
    social_score: PillarScore = Field(serialization_alias="socialScore")
    governance_score: PillarScore = Field(serialization_alias="governanceScore")
    department_ranking: list[DepartmentRankingItem] = Field(serialization_alias="departmentRanking")
    recent_carbon_transactions: list[RecentCarbonTransactionItem] = Field(
        serialization_alias="recentCarbonTransactions"
    )
    recent_activity: list[RecentActivityItem] = Field(serialization_alias="recentActivity")
    notifications: list[DashboardNotification] = Field(serialization_alias="notifications")
    goal_progress: list[GoalProgressItem] = Field(serialization_alias="goalProgress")
    monthly_carbon_trend: list[MonthlyCarbonTrendPoint] = Field(
        serialization_alias="monthlyCarbonTrend"
    )
    top_carbon_sources: list[TopCarbonSource] = Field(serialization_alias="topCarbonSources")
    quick_stats: list[QuickStatItem] = Field(serialization_alias="quickStats")
    quick_actions: list[QuickActionItem] = Field(serialization_alias="quickActions")
    top_performers: list[LeaderboardEntry] = Field(serialization_alias="topPerformers")
    xp_leaderboard: list[LeaderboardEntry] = Field(serialization_alias="xpLeaderboard")
    recent_badge_unlocks: list[EmployeeBadgeResponse] = Field(
        serialization_alias="recentBadgeUnlocks"
    )
    challenge_progress: list[ChallengeResponse] = Field(serialization_alias="challengeProgress")
