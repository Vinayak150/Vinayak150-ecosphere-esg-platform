from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.schemas import AuthenticatedUser
from app.modules.gamification.events import (
    publish_badge_unlocked,
    publish_challenge_completed,
    publish_participation_approved,
    publish_reward_redeemed,
)
from app.modules.gamification.models import (
    Badge,
    Challenge,
    ChallengeParticipation,
    ChallengeStatus,
    EmployeeBadge,
    ParticipationApproval,
    Reward,
    RewardRedemption,
    RewardStatus,
)
from app.modules.gamification.repository import GamificationRepository
from app.modules.gamification.schemas import (
    BadgeCreate,
    BadgeDistributionItem,
    BadgeResponse,
    BadgeUpdate,
    ChallengeCreate,
    ChallengeResponse,
    ChallengeUpdate,
    DepartmentLeaderboardEntry,
    EmployeeBadgeResponse,
    EmployeeOption,
    GamificationAnalyticsResponse,
    GamificationListParams,
    LeaderboardEntry,
    ParticipationCreate,
    ParticipationRejectionRequest,
    ParticipationResponse,
    ParticipationSubmit,
    RewardCreate,
    RewardRedemptionRequest,
    RewardRedemptionResponse,
    RewardResponse,
    RewardUpdate,
)
from app.modules.gamification.validators import (
    validate_active_challenge,
    validate_approval_proof,
    validate_challenge_create,
    validate_participation_for_review,
    validate_reward_redemption,
    validate_submission_proof,
    validate_unlock_rule,
)
from app.shared.exceptions.base import BusinessRuleViolationError, PermissionDeniedError
from app.shared.services.activity_log import ActivityLogService


class GamificationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repository = GamificationRepository(db)
        self._activity_log = ActivityLogService(db)

    def list_departments(self) -> list[dict[str, str]]:
        departments = self._repository.list_departments()
        return [{"id": str(d.id), "name": d.name, "code": d.code} for d in departments]

    def list_employees(self) -> list[EmployeeOption]:
        employees = self._repository.list_active_employees()
        department_ids = {emp.department_id for emp in employees if emp.department_id}
        department_names = self._repository.get_department_name_map(department_ids)
        xp_totals = dict(self._repository.get_employee_xp_totals())
        return [
            EmployeeOption(
                id=employee.id,
                name=f"{employee.first_name} {employee.last_name}",
                email=employee.email,
                department_name=department_names.get(employee.department_id)
                if employee.department_id
                else None,
                total_xp=xp_totals.get(employee.id, 0),
            )
            for employee in employees
        ]

    def list_challenges(
        self, params: GamificationListParams
    ) -> tuple[list[ChallengeResponse], dict[str, int]]:
        items, pagination = self._repository.list_challenges(params)
        challenge_ids = {item.id for item in items}
        stats = self._repository.get_participation_counts_for_challenges(challenge_ids)
        return [
            self._to_challenge_response(
                item, stats.get(item.id, {"total": 0, "approved": 0})
            )
            for item in items
        ], pagination

    def get_challenge(self, challenge_id: UUID) -> ChallengeResponse:
        challenge = self._repository.get_challenge(challenge_id)
        stats = self._repository.get_participation_counts_for_challenges({challenge.id})
        return self._to_challenge_response(
            challenge, stats.get(challenge.id, {"total": 0, "approved": 0})
        )

    def create_challenge(
        self, payload: ChallengeCreate, user: AuthenticatedUser
    ) -> ChallengeResponse:
        validate_challenge_create(payload)
        challenge = Challenge(**payload.model_dump())
        created = self._repository.create_challenge(challenge)
        self._log_mutation(user, "CREATE", "challenge", created.id)
        self._db.commit()
        return self.get_challenge(created.id)

    def update_challenge(
        self, challenge_id: UUID, payload: ChallengeUpdate, user: AuthenticatedUser
    ) -> ChallengeResponse:
        challenge = self._repository.get_challenge(challenge_id)
        updates = payload.model_dump(exclude_unset=True)
        if (
            "deadline" in updates
            and updates["deadline"] is not None
            and updates["deadline"] < date.today()
        ):
            from app.shared.exceptions.base import ValidationError

            raise ValidationError("Challenge deadline cannot be in the past")
        if "xp" in updates and updates["xp"] is not None and updates["xp"] < 0:
            from app.shared.exceptions.base import ValidationError

            raise ValidationError("XP must be zero or greater")

        previous_status = challenge.status
        for field, value in updates.items():
            setattr(challenge, field, value)

        updated = self._repository.update_challenge(challenge)
        self._log_mutation(user, "UPDATE", "challenge", updated.id)
        if (
            updated.status == ChallengeStatus.COMPLETED
            and previous_status != ChallengeStatus.COMPLETED
        ):
            publish_challenge_completed(
                {"challenge_id": str(updated.id), "title": updated.title, "xp": updated.xp}
            )
        self._db.commit()
        return self.get_challenge(updated.id)

    def delete_challenge(self, challenge_id: UUID, user: AuthenticatedUser) -> None:
        challenge = self._repository.get_challenge(challenge_id)
        self._repository.delete_challenge(challenge)
        self._log_mutation(user, "DELETE", "challenge", challenge_id)
        self._db.commit()

    def list_participations(
        self, params: GamificationListParams
    ) -> tuple[list[ParticipationResponse], dict[str, int]]:
        items, pagination = self._repository.list_participations(params)
        employee_ids = {item.employee_id for item in items}
        employee_names = self._repository.get_employee_name_map(employee_ids)
        department_names = self._repository.get_employee_department_map(employee_ids)
        return [
            self._to_participation_response(
                item,
                employee_names.get(item.employee_id),
                department_names.get(item.employee_id),
            )
            for item in items
        ], pagination

    def get_participation(self, participation_id: UUID) -> ParticipationResponse:
        participation = self._repository.get_participation(participation_id)
        employee_names = self._repository.get_employee_name_map({participation.employee_id})
        department_names = self._repository.get_employee_department_map(
            {participation.employee_id}
        )
        return self._to_participation_response(
            participation,
            employee_names.get(participation.employee_id),
            department_names.get(participation.employee_id),
        )

    def join_challenge(
        self, payload: ParticipationCreate, user: AuthenticatedUser
    ) -> ParticipationResponse:
        if user.employee_id is None:
            raise BusinessRuleViolationError("Authenticated user has no employee profile")

        challenge = self._repository.get_challenge(payload.challenge_id)
        validate_active_challenge(challenge)
        self._repository.get_employee(user.employee_id)

        participation = ChallengeParticipation(
            employee_id=user.employee_id,
            challenge_id=payload.challenge_id,
            approval_status=ParticipationApproval.PENDING,
        )
        created = self._repository.create_participation(participation)
        self._log_mutation(user, "CREATE", "challenge_participation", created.id)
        self._db.commit()
        return self.get_participation(created.id)

    def submit_participation(
        self,
        participation_id: UUID,
        payload: ParticipationSubmit,
        user: AuthenticatedUser,
    ) -> ParticipationResponse:
        participation = self._repository.get_participation(participation_id)
        self._ensure_participation_owner_or_manager(participation, user)

        if participation.approval_status in (
            ParticipationApproval.APPROVED,
            ParticipationApproval.REJECTED,
        ):
            raise BusinessRuleViolationError("Participation can no longer be submitted")

        challenge = participation.challenge
        validate_submission_proof(challenge, payload)

        participation.progress = payload.progress
        participation.proof_file = payload.proof_file
        participation.approval_status = ParticipationApproval.SUBMITTED
        updated = self._repository.update_participation(participation)
        self._log_mutation(user, "SUBMIT", "challenge_participation", updated.id)
        self._db.commit()
        return self.get_participation(updated.id)

    def approve_participation(
        self, participation_id: UUID, user: AuthenticatedUser
    ) -> ParticipationResponse:
        self._ensure_reviewer(user)
        participation = self._repository.get_participation(participation_id)
        challenge = participation.challenge

        validate_participation_for_review(participation.approval_status)
        validate_approval_proof(challenge, participation.proof_file)

        participation.approval_status = ParticipationApproval.APPROVED
        participation.xp_awarded = challenge.xp
        participation.completion_date = date.today()
        participation.rejection_reason = None
        updated = self._repository.update_participation(participation)
        self._log_mutation(user, "APPROVE", "challenge_participation", updated.id)
        publish_participation_approved(
            {
                "participation_id": str(updated.id),
                "employee_id": str(updated.employee_id),
                "xp_awarded": updated.xp_awarded,
            }
        )
        self._evaluate_badges(updated.employee_id)
        self._db.commit()
        return self.get_participation(updated.id)

    def reject_participation(
        self,
        participation_id: UUID,
        user: AuthenticatedUser,
        payload: ParticipationRejectionRequest | None = None,
    ) -> ParticipationResponse:
        self._ensure_reviewer(user)
        participation = self._repository.get_participation(participation_id)

        validate_participation_for_review(participation.approval_status)

        participation.approval_status = ParticipationApproval.REJECTED
        participation.xp_awarded = 0
        participation.completion_date = None
        participation.rejection_reason = (
            payload.rejection_reason if payload else None
        )
        updated = self._repository.update_participation(participation)
        self._log_mutation(user, "REJECT", "challenge_participation", updated.id)
        self._db.commit()
        return self.get_participation(updated.id)

    def delete_participation(self, participation_id: UUID, user: AuthenticatedUser) -> None:
        participation = self._repository.get_participation(participation_id)
        self._ensure_participation_owner_or_manager(participation, user)
        if (
            participation.approval_status == ParticipationApproval.APPROVED
            and not user.has_permission("challenges:write")
        ):
            raise PermissionDeniedError(
                "Approved participations require manager access to delete"
            )
        self._repository.delete_participation(participation)
        self._log_mutation(user, "DELETE", "challenge_participation", participation_id)
        self._db.commit()

    def list_badges(
        self, params: GamificationListParams
    ) -> tuple[list[BadgeResponse], dict[str, int]]:
        items, pagination = self._repository.list_badges(params)
        badge_ids = {item.id for item in items}
        earned_counts = self._repository.get_badge_earned_counts(badge_ids)
        return [
            self._to_badge_response(item, earned_counts.get(item.id, 0)) for item in items
        ], pagination

    def get_badge(self, badge_id: UUID) -> BadgeResponse:
        badge = self._repository.get_badge(badge_id)
        earned_counts = self._repository.get_badge_earned_counts({badge.id})
        return self._to_badge_response(badge, earned_counts.get(badge.id, 0))

    def create_badge(self, payload: BadgeCreate, user: AuthenticatedUser) -> BadgeResponse:
        validate_unlock_rule(payload.unlock_rule)
        badge = Badge(**payload.model_dump())
        created = self._repository.create_badge(badge)
        self._log_mutation(user, "CREATE", "badge", created.id)
        self._db.commit()
        return self.get_badge(created.id)

    def update_badge(
        self, badge_id: UUID, payload: BadgeUpdate, user: AuthenticatedUser
    ) -> BadgeResponse:
        badge = self._repository.get_badge(badge_id)
        updates = payload.model_dump(exclude_unset=True)
        if "unlock_rule" in updates and updates["unlock_rule"] is not None:
            validate_unlock_rule(updates["unlock_rule"])
        for field, value in updates.items():
            setattr(badge, field, value)
        updated = self._repository.update_badge(badge)
        self._log_mutation(user, "UPDATE", "badge", updated.id)
        self._db.commit()
        return self.get_badge(updated.id)

    def delete_badge(self, badge_id: UUID, user: AuthenticatedUser) -> None:
        badge = self._repository.get_badge(badge_id)
        self._repository.delete_badge(badge)
        self._log_mutation(user, "DELETE", "badge", badge_id)
        self._db.commit()

    def list_employee_badges(
        self, params: GamificationListParams
    ) -> tuple[list[EmployeeBadgeResponse], dict[str, int]]:
        items, pagination = self._repository.list_employee_badges(params)
        employee_ids = {item.employee_id for item in items}
        employee_names = self._repository.get_employee_name_map(employee_ids)
        return [
            EmployeeBadgeResponse(
                id=item.id,
                badge_id=item.badge_id,
                badge_name=item.badge.name if item.badge else None,
                badge_icon=item.badge.icon if item.badge else None,
                employee_id=item.employee_id,
                employee_name=employee_names.get(item.employee_id),
                earned_at=item.earned_at,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ], pagination

    def list_rewards(
        self, params: GamificationListParams
    ) -> tuple[list[RewardResponse], dict[str, int]]:
        items, pagination = self._repository.list_rewards(params)
        reward_ids = {item.id for item in items}
        redemption_counts = self._repository.get_reward_redemption_counts(reward_ids)
        return [
            self._to_reward_response(item, redemption_counts.get(item.id, 0)) for item in items
        ], pagination

    def get_reward(self, reward_id: UUID) -> RewardResponse:
        reward = self._repository.get_reward(reward_id)
        redemption_counts = self._repository.get_reward_redemption_counts({reward.id})
        return self._to_reward_response(reward, redemption_counts.get(reward.id, 0))

    def create_reward(self, payload: RewardCreate, user: AuthenticatedUser) -> RewardResponse:
        reward = Reward(**payload.model_dump())
        created = self._repository.create_reward(reward)
        self._log_mutation(user, "CREATE", "reward", created.id)
        self._db.commit()
        return self.get_reward(created.id)

    def update_reward(
        self, reward_id: UUID, payload: RewardUpdate, user: AuthenticatedUser
    ) -> RewardResponse:
        reward = self._repository.get_reward(reward_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(reward, field, value)
        if reward.stock <= 0 and reward.status == RewardStatus.ACTIVE:
            reward.status = RewardStatus.OUT_OF_STOCK
        elif reward.stock > 0 and reward.status == RewardStatus.OUT_OF_STOCK:
            reward.status = RewardStatus.ACTIVE
        updated = self._repository.update_reward(reward)
        self._log_mutation(user, "UPDATE", "reward", updated.id)
        self._db.commit()
        return self.get_reward(updated.id)

    def delete_reward(self, reward_id: UUID, user: AuthenticatedUser) -> None:
        reward = self._repository.get_reward(reward_id)
        self._repository.delete_reward(reward)
        self._log_mutation(user, "DELETE", "reward", reward_id)
        self._db.commit()

    def redeem_reward(
        self, payload: RewardRedemptionRequest, user: AuthenticatedUser
    ) -> RewardRedemptionResponse:
        if user.employee_id is None:
            raise BusinessRuleViolationError("Authenticated user has no employee profile")

        reward = self._repository.get_reward(payload.reward_id)
        if reward.status != RewardStatus.ACTIVE:
            raise BusinessRuleViolationError("Reward is not available for redemption")

        available_xp = self._repository.get_employee_xp(user.employee_id)
        validate_reward_redemption(available_xp, reward.points_required, reward.stock)

        reward.stock -= 1
        if reward.stock <= 0:
            reward.status = RewardStatus.OUT_OF_STOCK
        self._repository.update_reward(reward)

        redemption = RewardRedemption(
            reward_id=reward.id,
            employee_id=user.employee_id,
            redeemed_points=reward.points_required,
            redeemed_at=datetime.now(UTC),
        )
        created = self._repository.create_redemption(redemption)
        self._log_mutation(user, "REDEEM", "reward", reward.id)
        publish_reward_redeemed(
            {
                "redemption_id": str(created.id),
                "employee_id": str(user.employee_id),
                "reward_id": str(reward.id),
                "points": reward.points_required,
            }
        )
        self._db.commit()
        return self._to_redemption_response(created)

    def list_redemptions(
        self, params: GamificationListParams
    ) -> tuple[list[RewardRedemptionResponse], dict[str, int]]:
        items, pagination = self._repository.list_redemptions(params)
        employee_ids = {item.employee_id for item in items}
        employee_names = self._repository.get_employee_name_map(employee_ids)
        return [
            self._to_redemption_response(
                item, employee_names.get(item.employee_id)
            )
            for item in items
        ], pagination

    def get_company_leaderboard(self, limit: int = 20) -> list[LeaderboardEntry]:
        return self._build_leaderboard(limit=limit)

    def get_department_leaderboard(self, limit: int = 20) -> list[DepartmentLeaderboardEntry]:
        dept_totals = self._repository.get_department_xp_totals()
        entries: list[DepartmentLeaderboardEntry] = []
        for index, (dept_id, name, total_xp, employee_count) in enumerate(
            dept_totals[:limit], start=1
        ):
            average_xp = (
                (Decimal(total_xp) / Decimal(employee_count)).quantize(Decimal("0.01"))
                if employee_count > 0
                else Decimal("0")
            )
            entries.append(
                DepartmentLeaderboardEntry(
                    rank=index,
                    department_id=dept_id,
                    department_name=name,
                    total_xp=total_xp,
                    employee_count=employee_count,
                    average_xp=average_xp,
                )
            )
        return entries

    def get_analytics(self) -> GamificationAnalyticsResponse:
        total_challenges = (
            self._repository.count_challenges_by_status(ChallengeStatus.DRAFT)
            + self._repository.count_challenges_by_status(ChallengeStatus.ACTIVE)
            + self._repository.count_challenges_by_status(ChallengeStatus.UNDER_REVIEW)
            + self._repository.count_challenges_by_status(ChallengeStatus.COMPLETED)
            + self._repository.count_challenges_by_status(ChallengeStatus.ARCHIVED)
        )
        active_challenges = self._repository.count_challenges_by_status(ChallengeStatus.ACTIVE)
        completed_challenges = self._repository.count_challenges_by_status(
            ChallengeStatus.COMPLETED
        )
        approved = self._repository.count_participations_by_status(
            ParticipationApproval.APPROVED
        )
        total_participations = (
            approved
            + self._repository.count_participations_by_status(ParticipationApproval.PENDING)
            + self._repository.count_participations_by_status(ParticipationApproval.SUBMITTED)
            + self._repository.count_participations_by_status(ParticipationApproval.REJECTED)
        )
        completion_rate = (
            (Decimal(approved) / Decimal(total_participations) * Decimal("100")).quantize(
                Decimal("0.01")
            )
            if total_participations > 0
            else Decimal("0")
        )

        badge_distribution = [
            BadgeDistributionItem(
                badge_id=badge_id,
                badge_name=name,
                earned_count=count,
            )
            for badge_id, name, count in self._repository.get_badge_distribution()
        ]

        total_badge_awards = sum(item.earned_count for item in badge_distribution)

        return GamificationAnalyticsResponse(
            total_xp=self._repository.get_total_xp_awarded(),
            total_challenges=total_challenges,
            active_challenges=active_challenges,
            completed_challenges=completed_challenges,
            challenge_completion_rate=completion_rate,
            total_badges=len(self._repository.list_active_badges()),
            total_badge_awards=total_badge_awards,
            badge_distribution=badge_distribution,
            top_employees=self.get_company_leaderboard(limit=5),
            top_departments=self.get_department_leaderboard(limit=5),
            pending_reviews=self._repository.count_participations_by_status(
                ParticipationApproval.SUBMITTED
            ),
        )

    def get_top_performers(self, limit: int = 5) -> list[LeaderboardEntry]:
        return self.get_company_leaderboard(limit=limit)

    def get_xp_leaderboard(self, limit: int = 10) -> list[LeaderboardEntry]:
        return self.get_company_leaderboard(limit=limit)

    def get_recent_badge_unlocks(self, limit: int = 8) -> list[EmployeeBadgeResponse]:
        items = self._repository.get_recent_badge_unlocks(limit=limit)
        employee_ids = {item.employee_id for item in items}
        employee_names = self._repository.get_employee_name_map(employee_ids)
        return [
            EmployeeBadgeResponse(
                id=item.id,
                badge_id=item.badge_id,
                badge_name=item.badge.name if item.badge else None,
                badge_icon=item.badge.icon if item.badge else None,
                employee_id=item.employee_id,
                employee_name=employee_names.get(item.employee_id),
                earned_at=item.earned_at,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

    def get_challenge_progress(self, limit: int = 6) -> list[ChallengeResponse]:
        challenges = self._repository.get_challenge_progress_summary(limit=limit)
        stats = self._repository.get_participation_counts_for_challenges(
            {challenge.id for challenge in challenges}
        )
        return [
            self._to_challenge_response(
                challenge, stats.get(challenge.id, {"total": 0, "approved": 0})
            )
            for challenge in challenges
        ]

    def _build_leaderboard(self, limit: int = 20) -> list[LeaderboardEntry]:
        xp_totals = self._repository.get_employee_xp_totals()
        xp_totals.sort(key=lambda item: item[1], reverse=True)
        employee_ids = {employee_id for employee_id, _ in xp_totals[:limit]}
        employee_names = self._repository.get_employee_name_map(employee_ids)
        department_map = self._repository.get_employee_department_map(employee_ids)
        badge_counts = self._repository.get_employee_badge_counts(employee_ids)

        entries: list[LeaderboardEntry] = []
        for index, (employee_id, total_xp) in enumerate(xp_totals[:limit], start=1):
            dept_id, dept_name = department_map.get(employee_id, (None, None))
            entries.append(
                LeaderboardEntry(
                    rank=index,
                    employee_id=employee_id,
                    employee_name=employee_names.get(employee_id, "Unknown"),
                    department_id=dept_id,
                    department_name=dept_name,
                    total_xp=total_xp,
                    badge_count=badge_counts.get(employee_id, 0),
                )
            )
        return entries

    def _evaluate_badges(self, employee_id: UUID) -> None:
        badges = self._repository.list_active_badges()
        total_xp = self._repository.get_employee_xp(employee_id)
        approved_challenges = self._repository.count_approved_challenges(employee_id)
        existing_badge_ids = self._repository.get_employee_badge_ids(employee_id)

        for badge in badges:
            if badge.id in existing_badge_ids:
                continue
            if self._badge_criteria_met(badge, total_xp, approved_challenges):
                employee_badge = EmployeeBadge(
                    employee_id=employee_id,
                    badge_id=badge.id,
                    earned_at=datetime.now(UTC),
                )
                created = self._repository.create_employee_badge(employee_badge)
                publish_badge_unlocked(
                    {
                        "employee_id": str(employee_id),
                        "badge_id": str(badge.id),
                        "badge_name": badge.name,
                        "employee_badge_id": str(created.id),
                    }
                )

    def _badge_criteria_met(
        self, badge: Badge, total_xp: int, approved_challenges: int
    ) -> bool:
        rule = badge.unlock_rule or {}
        rule_type = rule.get("rule")
        threshold = rule.get("threshold")
        if not rule_type or threshold is None:
            return False
        if rule_type == "total_xp":
            return total_xp >= int(threshold)
        if rule_type == "approved_challenges":
            return approved_challenges >= int(threshold)
        return False

    def _to_challenge_response(
        self, challenge: Challenge, counts: dict[str, int]
    ) -> ChallengeResponse:
        return ChallengeResponse(
            id=challenge.id,
            title=challenge.title,
            category=challenge.category,
            description=challenge.description,
            xp=challenge.xp,
            difficulty=challenge.difficulty,
            evidence_required=challenge.evidence_required,
            deadline=challenge.deadline,
            status=challenge.status,
            participation_count=counts.get("total", 0),
            approved_count=counts.get("approved", 0),
            created_at=challenge.created_at,
            updated_at=challenge.updated_at,
        )

    def _to_participation_response(
        self,
        participation: ChallengeParticipation,
        employee_name: str | None,
        department_info: tuple[UUID | None, str | None] | None,
    ) -> ParticipationResponse:
        department_name = department_info[1] if department_info else None
        challenge = participation.challenge
        return ParticipationResponse(
            id=participation.id,
            employee_id=participation.employee_id,
            employee_name=employee_name,
            department_name=department_name,
            challenge_id=participation.challenge_id,
            challenge_title=challenge.title if challenge else None,
            progress=participation.progress,
            proof_file=participation.proof_file,
            approval_status=participation.approval_status,
            xp_awarded=participation.xp_awarded,
            completion_date=participation.completion_date,
            rejection_reason=participation.rejection_reason,
            created_at=participation.created_at,
            updated_at=participation.updated_at,
        )

    def _to_badge_response(self, badge: Badge, earned_count: int) -> BadgeResponse:
        return BadgeResponse(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            unlock_rule=badge.unlock_rule,
            icon=badge.icon,
            status=badge.status,
            earned_count=earned_count,
            created_at=badge.created_at,
            updated_at=badge.updated_at,
        )

    def _to_reward_response(self, reward: Reward, redemption_count: int) -> RewardResponse:
        return RewardResponse(
            id=reward.id,
            name=reward.name,
            description=reward.description,
            points_required=reward.points_required,
            stock=reward.stock,
            status=reward.status,
            redemption_count=redemption_count,
            created_at=reward.created_at,
            updated_at=reward.updated_at,
        )

    def _to_redemption_response(
        self,
        redemption: RewardRedemption,
        employee_name: str | None = None,
    ) -> RewardRedemptionResponse:
        reward = redemption.reward
        return RewardRedemptionResponse(
            id=redemption.id,
            reward_id=redemption.reward_id,
            reward_name=reward.name if reward else None,
            employee_id=redemption.employee_id,
            employee_name=employee_name,
            redeemed_points=redemption.redeemed_points,
            redeemed_at=redemption.redeemed_at,
            created_at=redemption.created_at,
            updated_at=redemption.updated_at,
        )

    def _ensure_reviewer(self, user: AuthenticatedUser) -> None:
        if not user.has_permission("challenges:write"):
            raise PermissionDeniedError(
                "Only authorized reviewers can approve challenge participation"
            )

    def _ensure_participation_owner_or_manager(
        self, participation: ChallengeParticipation, user: AuthenticatedUser
    ) -> None:
        if user.has_permission("challenges:write"):
            return
        if user.employee_id != participation.employee_id:
            raise PermissionDeniedError("You can only modify your own participation records")

    def _log_mutation(
        self,
        user: AuthenticatedUser,
        action: str,
        entity: str,
        entity_id: UUID,
    ) -> None:
        self._activity_log.log_mutation(
            employee_id=user.employee_id,
            user_id=user.id,
            action=action,
            entity=entity,
            entity_id=entity_id,
        )
