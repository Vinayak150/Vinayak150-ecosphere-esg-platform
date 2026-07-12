from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.auth.models import Department, Employee
from app.modules.gamification.models import (
    Badge,
    BadgeStatus,
    Challenge,
    ChallengeDifficulty,
    ChallengeParticipation,
    ChallengeStatus,
    EmployeeBadge,
    ParticipationApproval,
    Reward,
    RewardRedemption,
    RewardStatus,
)
from app.modules.gamification.schemas import GamificationListParams
from app.shared.exceptions.base import ConflictError, NotFoundError
from app.shared.models.base import EntityStatus
from app.shared.pagination.pagination import calculate_pagination
from app.shared.validators.enums import parse_enum_value


class GamificationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_employee(self, employee_id: UUID) -> Employee:
        employee = self._db.get(Employee, employee_id)
        if employee is None or employee.status != EntityStatus.ACTIVE:
            raise NotFoundError("Employee not found")
        return employee

    def get_challenge(self, challenge_id: UUID) -> Challenge:
        challenge = self._db.get(Challenge, challenge_id)
        if challenge is None:
            raise NotFoundError("Challenge not found")
        return challenge

    def get_participation(self, participation_id: UUID) -> ChallengeParticipation:
        stmt = (
            select(ChallengeParticipation)
            .options(joinedload(ChallengeParticipation.challenge))
            .where(ChallengeParticipation.id == participation_id)
        )
        participation = self._db.scalars(stmt).first()
        if participation is None:
            raise NotFoundError("Participation record not found")
        return participation

    def get_badge(self, badge_id: UUID) -> Badge:
        badge = self._db.get(Badge, badge_id)
        if badge is None:
            raise NotFoundError("Badge not found")
        return badge

    def get_reward(self, reward_id: UUID) -> Reward:
        reward = self._db.get(Reward, reward_id)
        if reward is None:
            raise NotFoundError("Reward not found")
        return reward

    def list_challenges(
        self, params: GamificationListParams
    ) -> tuple[list[Challenge], dict[str, int]]:
        query = select(Challenge)
        query = self._apply_challenge_filters(query, params)
        return self._paginate(query, params)

    def create_challenge(self, challenge: Challenge) -> Challenge:
        self._db.add(challenge)
        self._db.flush()
        return challenge

    def update_challenge(self, challenge: Challenge) -> Challenge:
        self._db.add(challenge)
        self._db.flush()
        return challenge

    def delete_challenge(self, challenge: Challenge) -> None:
        self._db.delete(challenge)
        self._db.flush()

    def get_participation_by_employee_challenge(
        self, employee_id: UUID, challenge_id: UUID
    ) -> ChallengeParticipation | None:
        stmt = select(ChallengeParticipation).where(
            ChallengeParticipation.employee_id == employee_id,
            ChallengeParticipation.challenge_id == challenge_id,
        )
        return self._db.scalars(stmt).first()

    def list_participations(
        self, params: GamificationListParams
    ) -> tuple[list[ChallengeParticipation], dict[str, int]]:
        query = select(ChallengeParticipation).options(
            joinedload(ChallengeParticipation.challenge)
        )
        if params.approval_status:
            approval = parse_enum_value(
                params.approval_status, ParticipationApproval, field_name="approval_status"
            )
            query = query.where(ChallengeParticipation.approval_status == approval)
        if params.challenge_id:
            query = query.where(ChallengeParticipation.challenge_id == params.challenge_id)
        if params.employee_id:
            query = query.where(ChallengeParticipation.employee_id == params.employee_id)
        if params.search:
            query = query.join(Challenge).where(
                Challenge.title.ilike(f"%{params.search}%")
            )
        sort_column = getattr(
            ChallengeParticipation,
            params.sort or "created_at",
            ChallengeParticipation.created_at,
        )
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        query = query.order_by(ordering)
        return self._paginate(query, params)

    def create_participation(
        self, participation: ChallengeParticipation
    ) -> ChallengeParticipation:
        existing = self.get_participation_by_employee_challenge(
            participation.employee_id, participation.challenge_id
        )
        if existing is not None:
            raise ConflictError("Employee has already joined this challenge")
        self._db.add(participation)
        self._db.flush()
        return participation

    def update_participation(
        self, participation: ChallengeParticipation
    ) -> ChallengeParticipation:
        self._db.add(participation)
        self._db.flush()
        return participation

    def delete_participation(self, participation: ChallengeParticipation) -> None:
        self._db.delete(participation)
        self._db.flush()

    def list_badges(
        self, params: GamificationListParams
    ) -> tuple[list[Badge], dict[str, int]]:
        query = select(Badge)
        if params.status:
            status = parse_enum_value(params.status, BadgeStatus)
            query = query.where(Badge.status == status)
        if params.search:
            query = query.where(Badge.name.ilike(f"%{params.search}%"))
        sort_column = getattr(Badge, params.sort or "created_at", Badge.created_at)
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        query = query.order_by(ordering)
        return self._paginate(query, params)

    def create_badge(self, badge: Badge) -> Badge:
        self._db.add(badge)
        self._db.flush()
        return badge

    def update_badge(self, badge: Badge) -> Badge:
        self._db.add(badge)
        self._db.flush()
        return badge

    def delete_badge(self, badge: Badge) -> None:
        self._db.delete(badge)
        self._db.flush()

    def list_employee_badges(
        self, params: GamificationListParams
    ) -> tuple[list[EmployeeBadge], dict[str, int]]:
        query = select(EmployeeBadge).options(joinedload(EmployeeBadge.badge))
        if params.employee_id:
            query = query.where(EmployeeBadge.employee_id == params.employee_id)
        query = query.order_by(desc(EmployeeBadge.earned_at))
        return self._paginate(query, params)

    def get_employee_badge(
        self, employee_id: UUID, badge_id: UUID
    ) -> EmployeeBadge | None:
        stmt = select(EmployeeBadge).where(
            EmployeeBadge.employee_id == employee_id,
            EmployeeBadge.badge_id == badge_id,
        )
        return self._db.scalars(stmt).first()

    def create_employee_badge(self, employee_badge: EmployeeBadge) -> EmployeeBadge:
        self._db.add(employee_badge)
        self._db.flush()
        return employee_badge

    def list_rewards(
        self, params: GamificationListParams
    ) -> tuple[list[Reward], dict[str, int]]:
        query = select(Reward)
        if params.status:
            status = parse_enum_value(params.status, RewardStatus)
            query = query.where(Reward.status == status)
        if params.search:
            query = query.where(Reward.name.ilike(f"%{params.search}%"))
        sort_column = getattr(Reward, params.sort or "created_at", Reward.created_at)
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        query = query.order_by(ordering)
        return self._paginate(query, params)

    def create_reward(self, reward: Reward) -> Reward:
        self._db.add(reward)
        self._db.flush()
        return reward

    def update_reward(self, reward: Reward) -> Reward:
        self._db.add(reward)
        self._db.flush()
        return reward

    def delete_reward(self, reward: Reward) -> None:
        self._db.delete(reward)
        self._db.flush()

    def create_redemption(self, redemption: RewardRedemption) -> RewardRedemption:
        self._db.add(redemption)
        self._db.flush()
        return redemption

    def list_redemptions(
        self, params: GamificationListParams
    ) -> tuple[list[RewardRedemption], dict[str, int]]:
        query = select(RewardRedemption).options(joinedload(RewardRedemption.reward))
        if params.employee_id:
            query = query.where(RewardRedemption.employee_id == params.employee_id)
        query = query.order_by(desc(RewardRedemption.redeemed_at))
        return self._paginate(query, params)

    def count_challenges_by_status(self, status: ChallengeStatus) -> int:
        return (
            self._db.scalar(
                select(func.count()).select_from(Challenge).where(Challenge.status == status)
            )
            or 0
        )

    def count_participations_by_status(self, status: ParticipationApproval) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(ChallengeParticipation)
                .where(ChallengeParticipation.approval_status == status)
            )
            or 0
        )

    def get_participation_counts_for_challenges(
        self, challenge_ids: set[UUID]
    ) -> dict[UUID, dict[str, int]]:
        if not challenge_ids:
            return {}
        rows = self._db.execute(
            select(
                ChallengeParticipation.challenge_id,
                ChallengeParticipation.approval_status,
                func.count(),
            )
            .where(ChallengeParticipation.challenge_id.in_(challenge_ids))
            .group_by(
                ChallengeParticipation.challenge_id,
                ChallengeParticipation.approval_status,
            )
        ).all()
        stats: dict[UUID, dict[str, int]] = {}
        for challenge_id, approval_status, count in rows:
            entry = stats.setdefault(challenge_id, {"total": 0, "approved": 0})
            entry["total"] += count
            if approval_status == ParticipationApproval.APPROVED:
                entry["approved"] += count
        return stats

    def get_badge_earned_counts(self, badge_ids: set[UUID]) -> dict[UUID, int]:
        if not badge_ids:
            return {}
        rows = self._db.execute(
            select(EmployeeBadge.badge_id, func.count())
            .where(EmployeeBadge.badge_id.in_(badge_ids))
            .group_by(EmployeeBadge.badge_id)
        ).all()
        return dict(rows)

    def get_reward_redemption_counts(self, reward_ids: set[UUID]) -> dict[UUID, int]:
        if not reward_ids:
            return {}
        rows = self._db.execute(
            select(RewardRedemption.reward_id, func.count())
            .where(RewardRedemption.reward_id.in_(reward_ids))
            .group_by(RewardRedemption.reward_id)
        ).all()
        return dict(rows)

    def get_employee_xp_totals(self) -> list[tuple[UUID, int]]:
        earned = (
            select(
                ChallengeParticipation.employee_id.label("employee_id"),
                func.coalesce(func.sum(ChallengeParticipation.xp_awarded), 0).label("earned"),
            )
            .where(ChallengeParticipation.approval_status == ParticipationApproval.APPROVED)
            .group_by(ChallengeParticipation.employee_id)
            .subquery()
        )
        spent = (
            select(
                RewardRedemption.employee_id.label("employee_id"),
                func.coalesce(func.sum(RewardRedemption.redeemed_points), 0).label("spent"),
            )
            .group_by(RewardRedemption.employee_id)
            .subquery()
        )
        rows = self._db.execute(
            select(
                Employee.id,
                func.coalesce(earned.c.earned, 0) - func.coalesce(spent.c.spent, 0),
            )
            .select_from(Employee)
            .outerjoin(earned, Employee.id == earned.c.employee_id)
            .outerjoin(spent, Employee.id == spent.c.employee_id)
            .where(Employee.status == EntityStatus.ACTIVE)
        ).all()
        return [(row[0], int(row[1] or 0)) for row in rows]

    def get_employee_xp(self, employee_id: UUID) -> int:
        earned = (
            self._db.scalar(
                select(func.coalesce(func.sum(ChallengeParticipation.xp_awarded), 0)).where(
                    ChallengeParticipation.employee_id == employee_id,
                    ChallengeParticipation.approval_status == ParticipationApproval.APPROVED,
                )
            )
            or 0
        )
        spent = (
            self._db.scalar(
                select(func.coalesce(func.sum(RewardRedemption.redeemed_points), 0)).where(
                    RewardRedemption.employee_id == employee_id
                )
            )
            or 0
        )
        return int(earned) - int(spent)

    def count_approved_challenges(self, employee_id: UUID) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(ChallengeParticipation)
                .where(
                    ChallengeParticipation.employee_id == employee_id,
                    ChallengeParticipation.approval_status == ParticipationApproval.APPROVED,
                )
            )
            or 0
        )

    def count_employee_badges(self, employee_id: UUID) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(EmployeeBadge)
                .where(EmployeeBadge.employee_id == employee_id)
            )
            or 0
        )

    def get_employee_badge_counts(self, employee_ids: set[UUID]) -> dict[UUID, int]:
        if not employee_ids:
            return {}
        rows = self._db.execute(
            select(EmployeeBadge.employee_id, func.count())
            .where(EmployeeBadge.employee_id.in_(employee_ids))
            .group_by(EmployeeBadge.employee_id)
        ).all()
        return dict(rows)

    def get_employee_badge_ids(self, employee_id: UUID) -> set[UUID]:
        rows = self._db.scalars(
            select(EmployeeBadge.badge_id).where(EmployeeBadge.employee_id == employee_id)
        ).all()
        return set(rows)

    def get_badge_distribution(self) -> list[tuple[UUID, str, int]]:
        rows = self._db.execute(
            select(Badge.id, Badge.name, func.count(EmployeeBadge.id))
            .outerjoin(EmployeeBadge, Badge.id == EmployeeBadge.badge_id)
            .where(Badge.status == BadgeStatus.ACTIVE)
            .group_by(Badge.id, Badge.name)
            .order_by(desc(func.count(EmployeeBadge.id)))
        ).all()
        return [(row[0], row[1], int(row[2] or 0)) for row in rows]

    def get_department_xp_totals(self) -> list[tuple[UUID, str, int, int]]:
        xp_by_employee = dict(self.get_employee_xp_totals())
        employees = self._db.scalars(
            select(Employee).where(Employee.status == EntityStatus.ACTIVE)
        ).all()
        dept_stats: dict[UUID, dict] = {}
        for employee in employees:
            if employee.department_id is None:
                continue
            xp = xp_by_employee.get(employee.id, 0)
            entry = dept_stats.setdefault(
                employee.department_id,
                {"total_xp": 0, "employee_count": 0},
            )
            entry["total_xp"] += xp
            entry["employee_count"] += 1

        if not dept_stats:
            return []

        dept_names = self.get_department_name_map(set(dept_stats.keys()))
        results = []
        for dept_id, stats in dept_stats.items():
            results.append(
                (
                    dept_id,
                    dept_names.get(dept_id, "Unknown"),
                    stats["total_xp"],
                    stats["employee_count"],
                )
            )
        results.sort(key=lambda item: item[2], reverse=True)
        return results

    def list_active_badges(self) -> list[Badge]:
        stmt = select(Badge).where(Badge.status == BadgeStatus.ACTIVE)
        return list(self._db.scalars(stmt).all())

    def list_departments(self) -> list[Department]:
        stmt = (
            select(Department)
            .where(Department.status == EntityStatus.ACTIVE)
            .order_by(Department.name)
        )
        return list(self._db.scalars(stmt).all())

    def count_active_employees(self) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(Employee)
                .where(Employee.status == EntityStatus.ACTIVE)
            )
            or 0
        )

    def list_active_employees(self) -> list[Employee]:
        stmt = (
            select(Employee)
            .where(Employee.status == EntityStatus.ACTIVE)
            .order_by(Employee.first_name, Employee.last_name)
        )
        return list(self._db.scalars(stmt).all())

    def get_employee_name_map(self, employee_ids: set[UUID]) -> dict[UUID, str]:
        if not employee_ids:
            return {}
        rows = self._db.execute(
            select(Employee.id, Employee.first_name, Employee.last_name).where(
                Employee.id.in_(employee_ids)
            )
        ).all()
        return {row[0]: f"{row[1]} {row[2]}" for row in rows}

    def get_employee_department_map(
        self, employee_ids: set[UUID]
    ) -> dict[UUID, tuple[UUID | None, str | None]]:
        if not employee_ids:
            return {}
        rows = self._db.execute(
            select(Employee.id, Employee.department_id, Department.name)
            .outerjoin(Department, Employee.department_id == Department.id)
            .where(Employee.id.in_(employee_ids))
        ).all()
        return {row[0]: (row[1], row[2]) for row in rows}

    def get_department_name_map(self, department_ids: set[UUID]) -> dict[UUID, str]:
        if not department_ids:
            return {}
        rows = self._db.execute(
            select(Department.id, Department.name).where(Department.id.in_(department_ids))
        ).all()
        return {row[0]: row[1] for row in rows}

    def get_recent_badge_unlocks(self, limit: int = 8) -> list[EmployeeBadge]:
        stmt = (
            select(EmployeeBadge)
            .options(joinedload(EmployeeBadge.badge))
            .order_by(desc(EmployeeBadge.earned_at))
            .limit(limit)
        )
        return list(self._db.scalars(stmt).all())

    def get_challenge_progress_summary(self, limit: int = 6) -> list[Challenge]:
        stmt = (
            select(Challenge)
            .where(
                Challenge.status.in_(
                    [ChallengeStatus.ACTIVE, ChallengeStatus.UNDER_REVIEW]
                )
            )
            .order_by(Challenge.deadline)
            .limit(limit)
        )
        return list(self._db.scalars(stmt).all())

    def get_total_xp_awarded(self) -> int:
        return int(
            self._db.scalar(
                select(func.coalesce(func.sum(ChallengeParticipation.xp_awarded), 0)).where(
                    ChallengeParticipation.approval_status == ParticipationApproval.APPROVED
                )
            )
            or 0
        )

    def _apply_challenge_filters(
        self, query: Select, params: GamificationListParams
    ) -> Select:
        if params.search:
            query = query.where(Challenge.title.ilike(f"%{params.search}%"))
        if params.status:
            status = parse_enum_value(params.status, ChallengeStatus)
            query = query.where(Challenge.status == status)
        if params.category:
            query = query.where(Challenge.category.ilike(f"%{params.category}%"))
        if params.difficulty:
            difficulty = parse_enum_value(
                params.difficulty, ChallengeDifficulty, field_name="difficulty"
            )
            query = query.where(Challenge.difficulty == difficulty)
        sort_column = getattr(Challenge, params.sort or "created_at", Challenge.created_at)
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        return query.order_by(ordering)

    def _paginate(self, query: Select, params: GamificationListParams) -> tuple[list, dict]:
        total = self._db.scalar(select(func.count()).select_from(query.subquery())) or 0
        pagination = calculate_pagination(params.page, params.page_size, total)
        items = list(
            self._db.scalars(
                query.offset((params.page - 1) * params.page_size).limit(params.page_size)
            ).all()
        )
        return items, pagination
