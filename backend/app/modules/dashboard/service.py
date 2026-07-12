from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.auth.permissions import PermissionCode
from app.auth.schemas import AuthenticatedUser
from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import (
    DashboardNotification,
    DashboardResponse,
    DepartmentRankingItem,
    PillarScore,
    QuickActionItem,
    QuickStatItem,
    RecentActivityItem,
    RecentCarbonTransactionItem,
)
from app.modules.environmental.models import GoalStatus
from app.modules.environmental.service import EnvironmentalService
from app.modules.gamification.service import GamificationService
from app.modules.governance.service import GovernanceService
from app.modules.social.service import SocialService


class DashboardService:
    QUICK_ACTION_DEFINITIONS = [
        {
            "id": "record-carbon",
            "label": "Record Carbon Transaction",
            "description": "Log a new carbon emission activity",
            "route": "/environmental",
            "permission": PermissionCode.CARBON_WRITE.value,
        },
        {
            "id": "view-environmental",
            "label": "Environmental Dashboard",
            "description": "View environmental metrics and goals",
            "route": "/environmental",
            "permission": PermissionCode.CARBON_READ.value,
        },
        {
            "id": "manage-goals",
            "label": "Manage Environmental Goals",
            "description": "Create or update department goals",
            "route": "/environmental",
            "permission": PermissionCode.CARBON_WRITE.value,
        },
        {
            "id": "export-reports",
            "label": "Export Reports",
            "description": "Generate ESG report exports",
            "route": "/",
            "permission": PermissionCode.REPORTS_EXPORT.value,
        },
        {
            "id": "view-social",
            "label": "CSR Dashboard",
            "description": "View CSR activities and participation",
            "route": "/social",
            "permission": PermissionCode.CSR_READ.value,
        },
        {
            "id": "join-csr",
            "label": "Join CSR Activity",
            "description": "Participate in a CSR initiative",
            "route": "/social",
            "permission": PermissionCode.CSR_PARTICIPATE.value,
        },
        {
            "id": "view-gamification",
            "label": "Gamification Hub",
            "description": "View challenges, badges, and leaderboards",
            "route": "/gamification",
            "permission": PermissionCode.CHALLENGES_READ.value,
        },
        {
            "id": "join-challenge",
            "label": "Join Challenge",
            "description": "Participate in an active challenge",
            "route": "/gamification",
            "permission": PermissionCode.CHALLENGES_PARTICIPATE.value,
        },
        {
            "id": "view-governance",
            "label": "Governance Dashboard",
            "description": "View policies, audits, and compliance",
            "route": "/governance",
            "permission": PermissionCode.POLICIES_READ.value,
        },
        {
            "id": "acknowledge-policy",
            "label": "Acknowledge Policy",
            "description": "Review and acknowledge governance policies",
            "route": "/governance",
            "permission": PermissionCode.POLICIES_ACKNOWLEDGE.value,
        },
    ]

    ENVIRONMENTAL_WEIGHT = Decimal("0.40")
    SOCIAL_WEIGHT = Decimal("0.30")
    GOVERNANCE_WEIGHT = Decimal("0.30")

    def __init__(self, db: Session) -> None:
        self._db = db
        self._environmental = EnvironmentalService(db)
        self._social = SocialService(db)
        self._governance = GovernanceService(db)
        self._gamification = GamificationService(db)
        self._repository = DashboardRepository(db)

    def get_dashboard(self, user: AuthenticatedUser) -> DashboardResponse:
        analytics = self._environmental.get_analytics()
        social_analytics = self._social.get_analytics()
        governance_analytics = self._governance.get_analytics()
        gamification_analytics = self._gamification.get_analytics()
        recent_transactions = self._environmental.get_recent_carbon_transactions(limit=8)
        entity_counts = self._environmental.get_entity_counts()
        avg_product_score = self._environmental.get_average_product_carbon_score()
        notification_goals = self._environmental.get_notification_goals()
        recent_activity_rows = self._repository.get_recent_activity(limit=12)

        environmental_score = self._compute_environmental_score(
            analytics.goal_progress, avg_product_score
        )
        department_ranking = self._build_department_ranking(
            analytics.department_carbon_totals,
            analytics.goal_progress,
        )

        social_score_value = social_analytics.social_score
        governance_score_value = governance_analytics.governance_score
        social_pillar = PillarScore(score=social_score_value, available=True, label="Social")
        governance_pillar = PillarScore(
            score=governance_score_value,
            available=True,
            label="Governance",
        )
        environmental_pillar = PillarScore(
            score=environmental_score,
            available=True,
            label="Environmental",
        )

        overall_esg = self._compute_overall_esg(
            environmental_score, social_score_value, governance_score_value
        )

        xp_leaderboard = self._gamification.get_xp_leaderboard(limit=10)

        return DashboardResponse(
            overall_esg=overall_esg,
            environmental_score=environmental_pillar,
            social_score=social_pillar,
            governance_score=governance_pillar,
            department_ranking=department_ranking,
            recent_carbon_transactions=[
                RecentCarbonTransactionItem(
                    id=tx.id,
                    activity_name=tx.activity_name,
                    department_name=tx.department_name,
                    emission_factor_name=tx.emission_factor_name,
                    calculated_emission=tx.calculated_emission,
                    transaction_date=tx.transaction_date,
                    created_at=tx.created_at,
                )
                for tx in recent_transactions
            ],
            recent_activity=[
                RecentActivityItem(
                    id=log.id,
                    action=log.action,
                    entity=log.entity,
                    entity_id=log.entity_id,
                    message=self._repository.get_activity_message(log, actor),
                    created_at=log.created_at,
                )
                for log, actor in recent_activity_rows
            ],
            notifications=self._build_notifications(
                notification_goals, social_analytics, governance_analytics, gamification_analytics
            ),
            goal_progress=analytics.goal_progress,
            monthly_carbon_trend=analytics.monthly_carbon_trend,
            top_carbon_sources=analytics.top_carbon_sources,
            quick_stats=self._build_quick_stats(
                analytics,
                entity_counts,
                social_analytics,
                governance_analytics,
                gamification_analytics,
            ),
            quick_actions=self._build_quick_actions(user),
            top_performers=xp_leaderboard[:5],
            xp_leaderboard=xp_leaderboard,
            recent_badge_unlocks=self._gamification.get_recent_badge_unlocks(limit=8),
            challenge_progress=self._gamification.get_challenge_progress(limit=6),
        )

    def _compute_environmental_score(
        self,
        goal_progress: list,
        avg_product_score: Decimal | None,
    ) -> Decimal:
        goal_values = [goal.progress_percentage for goal in goal_progress]
        goal_average = (
            sum(goal_values) / Decimal(len(goal_values)) if goal_values else Decimal("0")
        )

        if avg_product_score is not None:
            combined = goal_average * Decimal("0.6") + avg_product_score * Decimal("0.4")
        elif goal_values:
            combined = goal_average
        else:
            combined = Decimal("0")

        return combined.quantize(Decimal("0.01"))

    def _compute_overall_esg(
        self,
        environmental_score: Decimal,
        social_score: Decimal,
        governance_score: Decimal,
    ) -> Decimal:
        weighted = (
            environmental_score * self.ENVIRONMENTAL_WEIGHT
            + social_score * self.SOCIAL_WEIGHT
            + governance_score * self.GOVERNANCE_WEIGHT
        )
        return weighted.quantize(Decimal("0.01"))

    def _build_department_ranking(
        self,
        department_totals: list,
        goal_progress: list,
    ) -> list[DepartmentRankingItem]:
        if not department_totals:
            return []

        max_emission = max(
            (item.total_emission for item in department_totals), default=Decimal("0")
        )
        goals_by_department: dict = {}
        for goal in goal_progress:
            entry = goals_by_department.setdefault(
                goal.department_name,
                {"completed": 0, "total": 0, "progress_sum": Decimal("0")},
            )
            entry["total"] += 1
            entry["progress_sum"] += goal.progress_percentage
            if goal.status == GoalStatus.COMPLETED:
                entry["completed"] += 1

        rankings: list[DepartmentRankingItem] = []
        for item in department_totals:
            goal_data = goals_by_department.get(
                item.department_name,
                {"completed": 0, "total": 0, "progress_sum": Decimal("0")},
            )
            if max_emission > 0:
                emission_score = (
                    (Decimal("1") - (item.total_emission / max_emission)) * Decimal("100")
                ).quantize(Decimal("0.01"))
            else:
                emission_score = Decimal("100")

            goal_score = (
                (goal_data["progress_sum"] / Decimal(goal_data["total"])).quantize(Decimal("0.01"))
                if goal_data["total"] > 0
                else Decimal("0")
            )
            environmental_score = (
                emission_score * Decimal("0.5") + goal_score * Decimal("0.5")
            ).quantize(Decimal("0.01"))

            rankings.append(
                DepartmentRankingItem(
                    rank=0,
                    department_id=item.department_id,
                    department_name=item.department_name,
                    environmental_score=environmental_score,
                    total_emission=item.total_emission,
                    goals_completed=goal_data["completed"],
                    goals_total=goal_data["total"],
                )
            )

        rankings.sort(key=lambda entry: entry.environmental_score, reverse=True)
        return [
            entry.model_copy(update={"rank": index})
            for index, entry in enumerate(rankings, start=1)
        ]

    def _build_notifications(
        self, goals: list, social_analytics, governance_analytics, gamification_analytics
    ) -> list[DashboardNotification]:
        notifications: list[DashboardNotification] = []
        if governance_analytics.overdue_issues > 0:
            notifications.append(
                DashboardNotification(
                    id="governance-overdue-issues",
                    type="compliance_overdue",
                    title="Overdue compliance issues",
                    message=(
                        f"{governance_analytics.overdue_issues} compliance issues "
                        "are overdue and require attention"
                    ),
                    severity="high",
                    created_at=datetime.now(UTC),
                )
            )
        if governance_analytics.pending_acknowledgements > 0:
            notifications.append(
                DashboardNotification(
                    id="governance-policy-reminders",
                    type="policy_acknowledgement_reminder",
                    title="Policy acknowledgements pending",
                    message=(
                        f"{governance_analytics.pending_acknowledgements} policy "
                        "acknowledgements are still pending"
                    ),
                    severity="medium",
                    created_at=datetime.now(UTC),
                )
            )
        if gamification_analytics.pending_reviews > 0:
            notifications.append(
                DashboardNotification(
                    id="gamification-pending-reviews",
                    type="challenge_pending_review",
                    title="Challenge reviews pending",
                    message=(
                        f"{gamification_analytics.pending_reviews} challenge submissions "
                        "await approval"
                    ),
                    severity="medium",
                    created_at=datetime.now(UTC),
                )
            )
        if social_analytics.pending_approvals > 0:
            notifications.append(
                DashboardNotification(
                    id="social-pending-approvals",
                    type="csr_pending_approval",
                    title="CSR approvals pending",
                    message=(
                        f"{social_analytics.pending_approvals} "
                        "participation requests await approval"
                    ),
                    severity="medium",
                    created_at=datetime.now(UTC),
                )
            )
        for goal in goals:
            if goal.status == GoalStatus.OVERDUE:
                notifications.append(
                    DashboardNotification(
                        id=f"goal-overdue-{goal.id}",
                        type="goal_overdue",
                        title="Goal overdue",
                        message=(
                            f'"{goal.title}" passed its deadline on {goal.deadline.isoformat()}'
                        ),
                        severity="high",
                        created_at=datetime.combine(goal.deadline, datetime.min.time(), tzinfo=UTC),
                    )
                )
            else:
                notifications.append(
                    DashboardNotification(
                        id=f"goal-due-soon-{goal.id}",
                        type="goal_due_soon",
                        title="Goal deadline approaching",
                        message=f'"{goal.title}" is due on {goal.deadline.isoformat()}',
                        severity="medium",
                        created_at=goal.updated_at,
                    )
                )
        return notifications

    def _build_quick_stats(
        self,
        analytics,
        entity_counts: dict[str, int],
        social_analytics,
        governance_analytics,
        gamification_analytics,
    ) -> list[QuickStatItem]:
        return [
            QuickStatItem(
                key="total_emissions",
                label="Total Carbon Emissions",
                value=f"{analytics.total_emissions:.2f} kg CO₂",
            ),
            QuickStatItem(
                key="active_goals",
                label="Active Goals",
                value=str(analytics.active_goals),
            ),
            QuickStatItem(
                key="completed_goals",
                label="Completed Goals",
                value=str(analytics.completed_goals),
            ),
            QuickStatItem(
                key="departments",
                label="Departments Tracked",
                value=str(entity_counts["departments"]),
            ),
            QuickStatItem(
                key="carbon_transactions",
                label="Carbon Transactions",
                value=str(entity_counts["carbon_transactions"]),
            ),
            QuickStatItem(
                key="emission_factors",
                label="Emission Factors",
                value=str(entity_counts["emission_factors"]),
            ),
            QuickStatItem(
                key="social_score",
                label="Social Score",
                value=f"{social_analytics.social_score:.1f}%",
            ),
            QuickStatItem(
                key="csr_participation_rate",
                label="CSR Participation Rate",
                value=f"{social_analytics.participation_rate:.1f}%",
            ),
            QuickStatItem(
                key="active_csr_activities",
                label="Active CSR Activities",
                value=str(social_analytics.active_csr_activities),
            ),
            QuickStatItem(
                key="governance_score",
                label="Governance Score",
                value=f"{governance_analytics.governance_score:.1f}%",
            ),
            QuickStatItem(
                key="open_compliance_issues",
                label="Open Compliance Issues",
                value=str(governance_analytics.open_issues),
            ),
            QuickStatItem(
                key="policy_completion",
                label="Policy Completion",
                value=f"{governance_analytics.policy_completion:.1f}%",
            ),
            QuickStatItem(
                key="total_xp",
                label="Total XP Awarded",
                value=str(gamification_analytics.total_xp),
            ),
            QuickStatItem(
                key="active_challenges",
                label="Active Challenges",
                value=str(gamification_analytics.active_challenges),
            ),
            QuickStatItem(
                key="challenge_completion_rate",
                label="Challenge Completion Rate",
                value=f"{gamification_analytics.challenge_completion_rate:.1f}%",
            ),
            QuickStatItem(
                key="badge_awards",
                label="Badge Awards",
                value=str(gamification_analytics.total_badge_awards),
            ),
        ]

    def _build_quick_actions(self, user: AuthenticatedUser) -> list[QuickActionItem]:
        return [
            QuickActionItem(
                id=action["id"],
                label=action["label"],
                description=action["description"],
                route=action["route"],
                permission=action["permission"],
                enabled=user.has_permission(action["permission"]),
            )
            for action in self.QUICK_ACTION_DEFINITIONS
        ]
