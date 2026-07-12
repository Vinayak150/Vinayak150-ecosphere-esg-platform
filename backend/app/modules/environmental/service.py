from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.schemas import AuthenticatedUser
from app.modules.environmental.events import (
    publish_carbon_transaction_created,
    publish_goal_completed,
    publish_goal_updated,
)
from app.modules.environmental.models import (
    CarbonTransaction,
    EmissionFactor,
    EnvironmentalGoal,
    GoalStatus,
    ProductEsgProfile,
)
from app.modules.environmental.repository import EnvironmentalRepository
from app.modules.environmental.schemas import (
    CarbonCalculationRequest,
    CarbonCalculationResponse,
    CarbonTransactionCreate,
    CarbonTransactionResponse,
    CarbonTransactionUpdate,
    DepartmentCarbonTotal,
    EmissionFactorCreate,
    EmissionFactorResponse,
    EmissionFactorUpdate,
    EnvironmentalAnalyticsResponse,
    EnvironmentalGoalCreate,
    EnvironmentalGoalResponse,
    EnvironmentalGoalUpdate,
    EnvironmentalListParams,
    GoalProgressItem,
    MonthlyCarbonTrendPoint,
    ProductEsgCreate,
    ProductEsgResponse,
    ProductEsgUpdate,
    TopCarbonSource,
)
from app.modules.environmental.validators import (
    calculate_emission,
    validate_future_deadline,
    validate_positive_decimal,
    validate_score_range,
)
from app.shared.models.base import EntityStatus
from app.shared.services.activity_log import ActivityLogService


class EnvironmentalService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repository = EnvironmentalRepository(db)
        self._activity_log = ActivityLogService(db)

    def list_departments(self) -> list[dict[str, str]]:
        from sqlalchemy import select

        from app.auth.models import Department

        stmt = (
            select(Department)
            .where(Department.status == EntityStatus.ACTIVE)
            .order_by(Department.name)
        )
        departments = self._db.scalars(stmt).all()
        return [{"id": str(d.id), "name": d.name, "code": d.code} for d in departments]

    def list_emission_factors(
        self, params: EnvironmentalListParams
    ) -> tuple[list[EmissionFactorResponse], dict[str, int]]:
        items, pagination = self._repository.list_emission_factors(params)
        return [EmissionFactorResponse.model_validate(item) for item in items], pagination

    def get_emission_factor(self, factor_id: UUID) -> EmissionFactorResponse:
        factor = self._repository.get_emission_factor(factor_id)
        return EmissionFactorResponse.model_validate(factor)

    def create_emission_factor(
        self, payload: EmissionFactorCreate, user: AuthenticatedUser
    ) -> EmissionFactorResponse:
        validate_positive_decimal(payload.co2_factor, "Emission factor")
        factor = EmissionFactor(**payload.model_dump())
        created = self._repository.create_emission_factor(factor)
        self._log_mutation(user, "CREATE", "emission_factor", created.id)
        self._db.commit()
        return EmissionFactorResponse.model_validate(created)

    def update_emission_factor(
        self, factor_id: UUID, payload: EmissionFactorUpdate, user: AuthenticatedUser
    ) -> EmissionFactorResponse:
        factor = self._repository.get_emission_factor(factor_id)
        updates = payload.model_dump(exclude_unset=True)
        if "co2_factor" in updates and updates["co2_factor"] is not None:
            validate_positive_decimal(updates["co2_factor"], "Emission factor")
        for field, value in updates.items():
            setattr(factor, field, value)
        updated = self._repository.update_emission_factor(factor)
        self._log_mutation(user, "UPDATE", "emission_factor", updated.id)
        self._db.commit()
        return EmissionFactorResponse.model_validate(updated)

    def delete_emission_factor(self, factor_id: UUID, user: AuthenticatedUser) -> None:
        factor = self._repository.get_emission_factor(factor_id)
        self._repository.delete_emission_factor(factor)
        self._log_mutation(user, "DELETE", "emission_factor", factor_id)
        self._db.commit()

    def list_carbon_transactions(
        self, params: EnvironmentalListParams
    ) -> tuple[list[CarbonTransactionResponse], dict[str, int]]:
        items, pagination = self._repository.list_carbon_transactions(params)
        department_ids = {item.department_id for item in items}
        department_names = self._repository.get_department_name_map(department_ids)
        responses = [
            self._to_carbon_transaction_response(item, department_names.get(item.department_id))
            for item in items
        ]
        return responses, pagination

    def get_carbon_transaction(self, transaction_id: UUID) -> CarbonTransactionResponse:
        transaction = self._repository.get_carbon_transaction(transaction_id)
        department_names = self._repository.get_department_name_map({transaction.department_id})
        return self._to_carbon_transaction_response(
            transaction, department_names.get(transaction.department_id)
        )

    def create_carbon_transaction(
        self, payload: CarbonTransactionCreate, user: AuthenticatedUser
    ) -> CarbonTransactionResponse:
        self._repository.get_department(payload.department_id)
        factor = self._repository.get_emission_factor(payload.emission_factor_id)
        validate_positive_decimal(payload.quantity, "Quantity")
        calculated = calculate_emission(factor.co2_factor, payload.quantity)

        transaction = CarbonTransaction(
            **payload.model_dump(),
            calculated_emission=calculated,
        )
        created = self._repository.create_carbon_transaction(transaction)
        self._log_mutation(user, "CREATE", "carbon_transaction", created.id)
        publish_carbon_transaction_created(
            {
                "transaction_id": str(created.id),
                "department_id": str(created.department_id),
                "calculated_emission": float(created.calculated_emission),
            }
        )
        self._db.commit()
        self._db.refresh(created)
        department_names = self._repository.get_department_name_map({created.department_id})
        return self._to_carbon_transaction_response(
            created, department_names.get(created.department_id)
        )

    def update_carbon_transaction(
        self, transaction_id: UUID, payload: CarbonTransactionUpdate, user: AuthenticatedUser
    ) -> CarbonTransactionResponse:
        transaction = self._repository.get_carbon_transaction(transaction_id)
        updates = payload.model_dump(exclude_unset=True)

        if "department_id" in updates and updates["department_id"] is not None:
            self._repository.get_department(updates["department_id"])

        factor = transaction.emission_factor
        if "emission_factor_id" in updates and updates["emission_factor_id"] is not None:
            factor = self._repository.get_emission_factor(updates["emission_factor_id"])

        quantity = updates.get("quantity", transaction.quantity)
        if "quantity" in updates and updates["quantity"] is not None:
            validate_positive_decimal(updates["quantity"], "Quantity")

        for field, value in updates.items():
            setattr(transaction, field, value)

        transaction.calculated_emission = calculate_emission(factor.co2_factor, quantity)
        updated = self._repository.update_carbon_transaction(transaction)
        self._log_mutation(user, "UPDATE", "carbon_transaction", updated.id)
        self._db.commit()
        self._db.refresh(updated)
        department_names = self._repository.get_department_name_map({updated.department_id})
        return self._to_carbon_transaction_response(
            updated, department_names.get(updated.department_id)
        )

    def delete_carbon_transaction(self, transaction_id: UUID, user: AuthenticatedUser) -> None:
        transaction = self._repository.get_carbon_transaction(transaction_id)
        self._repository.delete_carbon_transaction(transaction)
        self._log_mutation(user, "DELETE", "carbon_transaction", transaction_id)
        self._db.commit()

    def calculate_carbon(self, payload: CarbonCalculationRequest) -> CarbonCalculationResponse:
        factor = self._repository.get_emission_factor(payload.emission_factor_id)
        calculated = calculate_emission(factor.co2_factor, payload.quantity)
        return CarbonCalculationResponse(
            emission_factor_id=factor.id,
            quantity=payload.quantity,
            co2_factor=factor.co2_factor,
            calculated_emission=calculated,
            unit=factor.unit,
        )

    def list_environmental_goals(
        self, params: EnvironmentalListParams
    ) -> tuple[list[EnvironmentalGoalResponse], dict[str, int]]:
        items, pagination = self._repository.list_environmental_goals(params)
        department_ids = {item.department_id for item in items}
        department_names = self._repository.get_department_name_map(department_ids)
        responses = [
            self._to_goal_response(item, department_names.get(item.department_id))
            for item in items
        ]
        return responses, pagination

    def get_environmental_goal(self, goal_id: UUID) -> EnvironmentalGoalResponse:
        goal = self._repository.get_environmental_goal(goal_id)
        department_names = self._repository.get_department_name_map({goal.department_id})
        return self._to_goal_response(goal, department_names.get(goal.department_id))

    def create_environmental_goal(
        self, payload: EnvironmentalGoalCreate, user: AuthenticatedUser
    ) -> EnvironmentalGoalResponse:
        self._repository.get_department(payload.department_id)
        validate_positive_decimal(payload.target_value, "Target value")
        validate_future_deadline(payload.deadline)

        goal = EnvironmentalGoal(**payload.model_dump())
        goal = self._apply_goal_status(goal)
        created = self._repository.create_environmental_goal(goal)
        self._log_mutation(user, "CREATE", "environmental_goal", created.id)
        publish_goal_updated(
            {
                "goal_id": str(created.id),
                "status": created.status.value,
                "current_value": float(created.current_value),
                "target_value": float(created.target_value),
            }
        )
        self._db.commit()
        department_names = self._repository.get_department_name_map({created.department_id})
        return self._to_goal_response(created, department_names.get(created.department_id))

    def update_environmental_goal(
        self, goal_id: UUID, payload: EnvironmentalGoalUpdate, user: AuthenticatedUser
    ) -> EnvironmentalGoalResponse:
        goal = self._repository.get_environmental_goal(goal_id)
        updates = payload.model_dump(exclude_unset=True)

        if "department_id" in updates and updates["department_id"] is not None:
            self._repository.get_department(updates["department_id"])
        if "target_value" in updates and updates["target_value"] is not None:
            validate_positive_decimal(updates["target_value"], "Target value")
        if "deadline" in updates and updates["deadline"] is not None:
            validate_future_deadline(updates["deadline"])

        previous_status = goal.status
        for field, value in updates.items():
            setattr(goal, field, value)

        goal = self._apply_goal_status(goal)
        updated = self._repository.update_environmental_goal(goal)
        self._log_mutation(user, "UPDATE", "environmental_goal", updated.id)
        publish_goal_updated(
            {
                "goal_id": str(updated.id),
                "status": updated.status.value,
                "current_value": float(updated.current_value),
                "target_value": float(updated.target_value),
            }
        )
        if updated.status == GoalStatus.COMPLETED and previous_status != GoalStatus.COMPLETED:
            publish_goal_completed(
                {
                    "goal_id": str(updated.id),
                    "department_id": str(updated.department_id),
                    "target_value": float(updated.target_value),
                }
            )
        self._db.commit()
        department_names = self._repository.get_department_name_map({updated.department_id})
        return self._to_goal_response(updated, department_names.get(updated.department_id))

    def delete_environmental_goal(self, goal_id: UUID, user: AuthenticatedUser) -> None:
        goal = self._repository.get_environmental_goal(goal_id)
        self._repository.delete_environmental_goal(goal)
        self._log_mutation(user, "DELETE", "environmental_goal", goal_id)
        self._db.commit()

    def list_product_esg_profiles(
        self, params: EnvironmentalListParams
    ) -> tuple[list[ProductEsgResponse], dict[str, int]]:
        items, pagination = self._repository.list_product_esg_profiles(params)
        return [ProductEsgResponse.model_validate(item) for item in items], pagination

    def get_product_esg_profile(self, profile_id: UUID) -> ProductEsgResponse:
        profile = self._repository.get_product_esg_profile(profile_id)
        return ProductEsgResponse.model_validate(profile)

    def create_product_esg_profile(
        self, payload: ProductEsgCreate, user: AuthenticatedUser
    ) -> ProductEsgResponse:
        validate_score_range(payload.carbon_score, "Carbon score")
        validate_score_range(payload.recyclability, "Recyclability")
        validate_score_range(payload.supplier_score, "Supplier score")
        profile = ProductEsgProfile(**payload.model_dump())
        created = self._repository.create_product_esg_profile(profile)
        self._log_mutation(user, "CREATE", "product_esg_profile", created.id)
        self._db.commit()
        return ProductEsgResponse.model_validate(created)

    def update_product_esg_profile(
        self, profile_id: UUID, payload: ProductEsgUpdate, user: AuthenticatedUser
    ) -> ProductEsgResponse:
        profile = self._repository.get_product_esg_profile(profile_id)
        updates = payload.model_dump(exclude_unset=True)
        for field in ("carbon_score", "recyclability", "supplier_score"):
            if field in updates and updates[field] is not None:
                validate_score_range(updates[field], field.replace("_", " ").title())
        for field, value in updates.items():
            setattr(profile, field, value)
        updated = self._repository.update_product_esg_profile(profile)
        self._log_mutation(user, "UPDATE", "product_esg_profile", updated.id)
        self._db.commit()
        return ProductEsgResponse.model_validate(updated)

    def delete_product_esg_profile(self, profile_id: UUID, user: AuthenticatedUser) -> None:
        profile = self._repository.get_product_esg_profile(profile_id)
        self._repository.delete_product_esg_profile(profile)
        self._log_mutation(user, "DELETE", "product_esg_profile", profile_id)
        self._db.commit()

    def get_analytics(self) -> EnvironmentalAnalyticsResponse:
        department_totals = [
            DepartmentCarbonTotal(
                department_id=dept_id,
                department_name=name,
                total_emission=total,
            )
            for dept_id, name, total in self._repository.get_department_carbon_totals()
        ]
        monthly_trend = [
            MonthlyCarbonTrendPoint(month=month, total_emission=total)
            for month, total in self._repository.get_monthly_carbon_trend()
        ]
        top_sources = [
            TopCarbonSource(
                source_type=source_type,
                emission_factor_name=factor_name,
                total_emission=total,
            )
            for source_type, factor_name, total in self._repository.get_top_carbon_sources()
        ]

        goals, _ = self._repository.list_environmental_goals(
            EnvironmentalListParams(page=1, page_size=100)
        )
        department_ids = {goal.department_id for goal in goals}
        department_names = self._repository.get_department_name_map(department_ids)
        goal_progress = [
            GoalProgressItem(
                goal_id=goal.id,
                title=goal.title,
                department_name=department_names.get(goal.department_id, "Unknown"),
                current_value=goal.current_value,
                target_value=goal.target_value,
                progress_percentage=self._calculate_progress(goal.current_value, goal.target_value),
                status=goal.status,
                deadline=goal.deadline,
            )
            for goal in goals
        ]

        return EnvironmentalAnalyticsResponse(
            department_carbon_totals=department_totals,
            monthly_carbon_trend=monthly_trend,
            top_carbon_sources=top_sources,
            goal_progress=goal_progress,
            total_emissions=self._repository.get_total_emissions(),
            active_goals=self._repository.count_goals_by_status(GoalStatus.IN_PROGRESS)
            + self._repository.count_goals_by_status(GoalStatus.NOT_STARTED),
            completed_goals=self._repository.count_goals_by_status(GoalStatus.COMPLETED),
        )

    def get_recent_carbon_transactions(self, limit: int = 10) -> list[CarbonTransactionResponse]:
        transactions = self._repository.get_recent_carbon_transactions(limit)
        department_ids = {tx.department_id for tx in transactions}
        department_names = self._repository.get_department_name_map(department_ids)
        return [
            self._to_carbon_transaction_response(tx, department_names.get(tx.department_id))
            for tx in transactions
        ]

    def get_average_product_carbon_score(self) -> Decimal | None:
        return self._repository.get_average_product_carbon_score()

    def get_entity_counts(self) -> dict[str, int]:
        return self._repository.count_active_entities()

    def get_notification_goals(self) -> list[EnvironmentalGoal]:
        return self._repository.get_goals_for_notifications()

    def _to_carbon_transaction_response(
        self, transaction: CarbonTransaction, department_name: str | None
    ) -> CarbonTransactionResponse:
        return CarbonTransactionResponse(
            id=transaction.id,
            department_id=transaction.department_id,
            department_name=department_name,
            emission_factor_id=transaction.emission_factor_id,
            emission_factor_name=transaction.emission_factor.name
            if transaction.emission_factor
            else None,
            activity_name=transaction.activity_name,
            quantity=transaction.quantity,
            unit=transaction.unit,
            calculated_emission=transaction.calculated_emission,
            transaction_date=transaction.transaction_date,
            status=transaction.status,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )

    def _to_goal_response(
        self, goal: EnvironmentalGoal, department_name: str | None
    ) -> EnvironmentalGoalResponse:
        return EnvironmentalGoalResponse(
            id=goal.id,
            department_id=goal.department_id,
            department_name=department_name,
            title=goal.title,
            target_value=goal.target_value,
            current_value=goal.current_value,
            progress_percentage=self._calculate_progress(goal.current_value, goal.target_value),
            deadline=goal.deadline,
            status=goal.status,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )

    def _calculate_progress(self, current: Decimal, target: Decimal) -> Decimal:
        if target <= 0:
            return Decimal("0")
        progress = (current / target * Decimal("100")).quantize(Decimal("0.01"))
        return min(progress, Decimal("100"))

    def _apply_goal_status(self, goal: EnvironmentalGoal) -> EnvironmentalGoal:
        from datetime import date

        if goal.current_value >= goal.target_value:
            goal.status = GoalStatus.COMPLETED
        elif goal.deadline < date.today():
            goal.status = GoalStatus.OVERDUE
        elif goal.current_value > 0:
            goal.status = GoalStatus.IN_PROGRESS
        else:
            goal.status = GoalStatus.NOT_STARTED
        return goal

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
