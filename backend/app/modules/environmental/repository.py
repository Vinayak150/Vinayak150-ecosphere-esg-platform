from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.auth.models import Department
from app.modules.environmental.models import (
    CarbonTransaction,
    EmissionFactor,
    EnvironmentalGoal,
    GoalStatus,
    ProductEsgProfile,
    TransactionStatus,
)
from app.modules.environmental.schemas import EnvironmentalListParams
from app.shared.exceptions.base import NotFoundError
from app.shared.models.base import EntityStatus
from app.shared.pagination.pagination import calculate_pagination
from app.shared.validators.enums import parse_enum_value

_STATUS_ENUMS = {
    EmissionFactor: EntityStatus,
    ProductEsgProfile: EntityStatus,
    CarbonTransaction: TransactionStatus,
    EnvironmentalGoal: GoalStatus,
}


class EnvironmentalRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_department(self, department_id: UUID) -> Department:
        department = self._db.get(Department, department_id)
        if department is None or department.status != EntityStatus.ACTIVE:
            raise NotFoundError("Department not found")
        return department

    def get_emission_factor(self, factor_id: UUID) -> EmissionFactor:
        factor = self._db.get(EmissionFactor, factor_id)
        if factor is None:
            raise NotFoundError("Emission factor not found")
        return factor

    def list_emission_factors(
        self, params: EnvironmentalListParams
    ) -> tuple[list[EmissionFactor], dict[str, int]]:
        query = select(EmissionFactor)
        query = self._apply_common_filters(query, EmissionFactor, params)
        if params.source_type:
            query = query.where(EmissionFactor.source_type.ilike(f"%{params.source_type}%"))
        return self._paginate(query, params)

    def create_emission_factor(self, factor: EmissionFactor) -> EmissionFactor:
        self._db.add(factor)
        self._db.flush()
        return factor

    def update_emission_factor(self, factor: EmissionFactor) -> EmissionFactor:
        self._db.add(factor)
        self._db.flush()
        return factor

    def delete_emission_factor(self, factor: EmissionFactor) -> None:
        self._db.delete(factor)
        self._db.flush()

    def get_carbon_transaction(self, transaction_id: UUID) -> CarbonTransaction:
        stmt = (
            select(CarbonTransaction)
            .options(joinedload(CarbonTransaction.emission_factor))
            .where(CarbonTransaction.id == transaction_id)
        )
        transaction = self._db.scalars(stmt).first()
        if transaction is None:
            raise NotFoundError("Carbon transaction not found")
        return transaction

    def list_carbon_transactions(
        self, params: EnvironmentalListParams
    ) -> tuple[list[CarbonTransaction], dict[str, int]]:
        query = select(CarbonTransaction).options(joinedload(CarbonTransaction.emission_factor))
        query = self._apply_common_filters(query, CarbonTransaction, params)
        if params.department_id:
            query = query.where(CarbonTransaction.department_id == params.department_id)
        if params.start_date:
            query = query.where(CarbonTransaction.transaction_date >= params.start_date)
        if params.end_date:
            query = query.where(CarbonTransaction.transaction_date <= params.end_date)
        return self._paginate(query, params)

    def create_carbon_transaction(self, transaction: CarbonTransaction) -> CarbonTransaction:
        self._db.add(transaction)
        self._db.flush()
        return transaction

    def update_carbon_transaction(self, transaction: CarbonTransaction) -> CarbonTransaction:
        self._db.add(transaction)
        self._db.flush()
        return transaction

    def delete_carbon_transaction(self, transaction: CarbonTransaction) -> None:
        self._db.delete(transaction)
        self._db.flush()

    def get_environmental_goal(self, goal_id: UUID) -> EnvironmentalGoal:
        goal = self._db.get(EnvironmentalGoal, goal_id)
        if goal is None:
            raise NotFoundError("Environmental goal not found")
        return goal

    def list_environmental_goals(
        self, params: EnvironmentalListParams
    ) -> tuple[list[EnvironmentalGoal], dict[str, int]]:
        query = select(EnvironmentalGoal)
        query = self._apply_common_filters(query, EnvironmentalGoal, params)
        if params.department_id:
            query = query.where(EnvironmentalGoal.department_id == params.department_id)
        return self._paginate(query, params)

    def create_environmental_goal(self, goal: EnvironmentalGoal) -> EnvironmentalGoal:
        self._db.add(goal)
        self._db.flush()
        return goal

    def update_environmental_goal(self, goal: EnvironmentalGoal) -> EnvironmentalGoal:
        self._db.add(goal)
        self._db.flush()
        return goal

    def delete_environmental_goal(self, goal: EnvironmentalGoal) -> None:
        self._db.delete(goal)
        self._db.flush()

    def get_product_esg_profile(self, profile_id: UUID) -> ProductEsgProfile:
        profile = self._db.get(ProductEsgProfile, profile_id)
        if profile is None:
            raise NotFoundError("Product ESG profile not found")
        return profile

    def list_product_esg_profiles(
        self, params: EnvironmentalListParams
    ) -> tuple[list[ProductEsgProfile], dict[str, int]]:
        query = select(ProductEsgProfile)
        query = self._apply_common_filters(query, ProductEsgProfile, params)
        return self._paginate(query, params)

    def create_product_esg_profile(self, profile: ProductEsgProfile) -> ProductEsgProfile:
        self._db.add(profile)
        self._db.flush()
        return profile

    def update_product_esg_profile(self, profile: ProductEsgProfile) -> ProductEsgProfile:
        self._db.add(profile)
        self._db.flush()
        return profile

    def delete_product_esg_profile(self, profile: ProductEsgProfile) -> None:
        self._db.delete(profile)
        self._db.flush()

    def get_department_name_map(self, department_ids: set[UUID]) -> dict[UUID, str]:
        if not department_ids:
            return {}
        stmt = select(Department.id, Department.name).where(Department.id.in_(department_ids))
        return {row.id: row.name for row in self._db.execute(stmt).all()}

    def get_department_carbon_totals(self) -> list[tuple[UUID, str, Decimal]]:
        stmt = (
            select(
                Department.id,
                Department.name,
                func.coalesce(func.sum(CarbonTransaction.calculated_emission), 0),
            )
            .join(CarbonTransaction, CarbonTransaction.department_id == Department.id)
            .where(CarbonTransaction.status == TransactionStatus.ACTIVE)
            .group_by(Department.id, Department.name)
            .order_by(desc(func.sum(CarbonTransaction.calculated_emission)))
        )
        return [(row[0], row[1], Decimal(row[2])) for row in self._db.execute(stmt).all()]

    def get_monthly_carbon_trend(self) -> list[tuple[str, Decimal]]:
        month_label = func.to_char(CarbonTransaction.transaction_date, "YYYY-MM")
        stmt = (
            select(
                month_label,
                func.coalesce(func.sum(CarbonTransaction.calculated_emission), 0),
            )
            .where(CarbonTransaction.status == TransactionStatus.ACTIVE)
            .group_by(month_label)
            .order_by(month_label)
        )
        return [(row[0], Decimal(row[1])) for row in self._db.execute(stmt).all()]

    def get_top_carbon_sources(self, limit: int = 5) -> list[tuple[str, str, Decimal]]:
        stmt = (
            select(
                EmissionFactor.source_type,
                EmissionFactor.name,
                func.coalesce(func.sum(CarbonTransaction.calculated_emission), 0),
            )
            .join(EmissionFactor, CarbonTransaction.emission_factor_id == EmissionFactor.id)
            .where(CarbonTransaction.status == TransactionStatus.ACTIVE)
            .group_by(EmissionFactor.source_type, EmissionFactor.name)
            .order_by(desc(func.sum(CarbonTransaction.calculated_emission)))
            .limit(limit)
        )
        return [(row[0], row[1], Decimal(row[2])) for row in self._db.execute(stmt).all()]

    def get_total_emissions(self) -> Decimal:
        stmt = select(func.coalesce(func.sum(CarbonTransaction.calculated_emission), 0)).where(
            CarbonTransaction.status == TransactionStatus.ACTIVE
        )
        total = self._db.scalar(stmt)
        return Decimal(total or 0)

    def count_goals_by_status(self, status: GoalStatus) -> int:
        stmt = (
            select(func.count())
            .select_from(EnvironmentalGoal)
            .where(EnvironmentalGoal.status == status)
        )
        return int(self._db.scalar(stmt) or 0)

    def get_recent_carbon_transactions(self, limit: int = 10) -> list[CarbonTransaction]:
        stmt = (
            select(CarbonTransaction)
            .options(joinedload(CarbonTransaction.emission_factor))
            .where(CarbonTransaction.status == TransactionStatus.ACTIVE)
            .order_by(desc(CarbonTransaction.transaction_date), desc(CarbonTransaction.created_at))
            .limit(limit)
        )
        return list(self._db.scalars(stmt).all())

    def get_average_product_carbon_score(self) -> Decimal | None:
        stmt = select(func.avg(ProductEsgProfile.carbon_score)).where(
            ProductEsgProfile.status == EntityStatus.ACTIVE
        )
        average = self._db.scalar(stmt)
        return Decimal(average).quantize(Decimal("0.01")) if average is not None else None

    def count_active_entities(self) -> dict[str, int]:
        emission_factors = self._db.scalar(
            select(func.count())
            .select_from(EmissionFactor)
            .where(EmissionFactor.status == EntityStatus.ACTIVE)
        )
        carbon_transactions = self._db.scalar(
            select(func.count())
            .select_from(CarbonTransaction)
            .where(CarbonTransaction.status == TransactionStatus.ACTIVE)
        )
        products = self._db.scalar(
            select(func.count())
            .select_from(ProductEsgProfile)
            .where(ProductEsgProfile.status == EntityStatus.ACTIVE)
        )
        departments = self._db.scalar(
            select(func.count())
            .select_from(Department)
            .where(Department.status == EntityStatus.ACTIVE)
        )
        return {
            "emission_factors": int(emission_factors or 0),
            "carbon_transactions": int(carbon_transactions or 0),
            "products": int(products or 0),
            "departments": int(departments or 0),
        }

    def get_goals_for_notifications(self) -> list[EnvironmentalGoal]:
        from datetime import date, timedelta

        due_soon = date.today() + timedelta(days=7)
        stmt = (
            select(EnvironmentalGoal)
            .where(
                (EnvironmentalGoal.status == GoalStatus.OVERDUE)
                | (
                    (EnvironmentalGoal.deadline <= due_soon)
                    & (EnvironmentalGoal.status != GoalStatus.COMPLETED)
                )
            )
            .order_by(EnvironmentalGoal.deadline)
            .limit(10)
        )
        return list(self._db.scalars(stmt).all())

    def _apply_common_filters(
        self, query: Select, model, params: EnvironmentalListParams
    ) -> Select:
        if params.search:
            if hasattr(model, "name"):
                query = query.where(model.name.ilike(f"%{params.search}%"))
            elif hasattr(model, "title"):
                query = query.where(model.title.ilike(f"%{params.search}%"))
            elif hasattr(model, "product_name"):
                query = query.where(model.product_name.ilike(f"%{params.search}%"))
            elif hasattr(model, "activity_name"):
                query = query.where(model.activity_name.ilike(f"%{params.search}%"))

        if params.status and hasattr(model, "status"):
            status_enum = _STATUS_ENUMS.get(model)
            if status_enum is not None:
                status = parse_enum_value(params.status, status_enum)
                query = query.where(model.status == status)

        sort_column = getattr(model, params.sort or "created_at", model.created_at)
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        return query.order_by(ordering)

    def _paginate(
        self, query: Select, params: EnvironmentalListParams
    ) -> tuple[list, dict[str, int]]:
        total = self._db.scalar(select(func.count()).select_from(query.subquery())) or 0
        offset = (params.page - 1) * params.page_size
        items = list(self._db.scalars(query.offset(offset).limit(params.page_size)).all())
        return items, calculate_pagination(params.page, params.page_size, total)
