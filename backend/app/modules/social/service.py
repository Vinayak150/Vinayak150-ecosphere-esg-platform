from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.schemas import AuthenticatedUser
from app.modules.social.events import (
    publish_csr_activity_completed,
    publish_csr_participation_approved,
    publish_csr_participation_rejected,
)
from app.modules.social.models import (
    ApprovalStatus,
    CsrActivity,
    CSRActivityStatus,
    EmployeeParticipation,
)
from app.modules.social.repository import SocialRepository
from app.modules.social.schemas import (
    CsrActivityCreate,
    CsrActivityResponse,
    CsrActivityUpdate,
    DepartmentParticipationItem,
    EmployeeOption,
    MonthlyCsrTrendPoint,
    ParticipationCreate,
    ParticipationResponse,
    ParticipationUpdate,
    SocialAnalyticsResponse,
    SocialListParams,
    TopParticipatingDepartment,
)
from app.modules.social.validators import (
    validate_active_csr_activity,
    validate_approval_proof,
    validate_date_range,
    validate_positive_points,
)
from app.shared.exceptions.base import BusinessRuleViolationError, PermissionDeniedError
from app.shared.services.activity_log import ActivityLogService


class SocialService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repository = SocialRepository(db)
        self._activity_log = ActivityLogService(db)

    def list_employees(self) -> list[EmployeeOption]:
        employees = self._repository.list_active_employees()
        department_ids = {emp.department_id for emp in employees if emp.department_id}
        department_names = self._repository.get_department_name_map(department_ids)
        return [
            EmployeeOption(
                id=employee.id,
                name=f"{employee.first_name} {employee.last_name}",
                email=employee.email,
                department_name=department_names.get(employee.department_id)
                if employee.department_id
                else None,
            )
            for employee in employees
        ]

    def list_departments(self) -> list[dict[str, str]]:
        departments = self._repository.list_departments()
        return [{"id": str(d.id), "name": d.name, "code": d.code} for d in departments]

    def list_csr_activities(
        self, params: SocialListParams
    ) -> tuple[list[CsrActivityResponse], dict[str, int]]:
        items, pagination = self._repository.list_csr_activities(params)
        activity_ids = {item.id for item in items}
        department_ids = {item.department_id for item in items}
        department_names = self._repository.get_department_name_map(department_ids)
        counts = self._repository.get_participation_counts_for_activities(activity_ids)
        responses = [
            self._to_csr_activity_response(
                item,
                department_names.get(item.department_id),
                counts.get(item.id, {"total": 0, "approved": 0}),
            )
            for item in items
        ]
        return responses, pagination

    def get_csr_activity(self, activity_id: UUID) -> CsrActivityResponse:
        activity = self._repository.get_csr_activity(activity_id)
        department_names = self._repository.get_department_name_map({activity.department_id})
        counts = self._repository.get_participation_counts_for_activities({activity.id})
        return self._to_csr_activity_response(
            activity,
            department_names.get(activity.department_id),
            counts.get(activity.id, {"total": 0, "approved": 0}),
        )

    def create_csr_activity(
        self, payload: CsrActivityCreate, user: AuthenticatedUser
    ) -> CsrActivityResponse:
        self._repository.get_department(payload.department_id)
        validate_date_range(payload.start_date, payload.end_date)
        validate_positive_points(payload.points)
        activity = CsrActivity(**payload.model_dump())
        created = self._repository.create_csr_activity(activity)
        self._log_mutation(user, "CREATE", "csr_activity", created.id)
        self._db.commit()
        return self.get_csr_activity(created.id)

    def update_csr_activity(
        self, activity_id: UUID, payload: CsrActivityUpdate, user: AuthenticatedUser
    ) -> CsrActivityResponse:
        activity = self._repository.get_csr_activity(activity_id)
        updates = payload.model_dump(exclude_unset=True)
        if "department_id" in updates and updates["department_id"] is not None:
            self._repository.get_department(updates["department_id"])
        if "points" in updates and updates["points"] is not None:
            validate_positive_points(updates["points"])

        start_date = updates.get("start_date", activity.start_date)
        end_date = updates.get("end_date", activity.end_date)
        if "start_date" in updates or "end_date" in updates:
            validate_date_range(start_date, end_date)

        previous_status = activity.status
        for field, value in updates.items():
            setattr(activity, field, value)

        updated = self._repository.update_csr_activity(activity)
        self._log_mutation(user, "UPDATE", "csr_activity", updated.id)
        if (
            updated.status == CSRActivityStatus.COMPLETED
            and previous_status != CSRActivityStatus.COMPLETED
        ):
            publish_csr_activity_completed(
                {"activity_id": str(updated.id), "title": updated.title}
            )
        self._db.commit()
        return self.get_csr_activity(updated.id)

    def delete_csr_activity(self, activity_id: UUID, user: AuthenticatedUser) -> None:
        activity = self._repository.get_csr_activity(activity_id)
        self._repository.delete_csr_activity(activity)
        self._log_mutation(user, "DELETE", "csr_activity", activity_id)
        self._db.commit()

    def list_participations(
        self, params: SocialListParams
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
        department_names = self._repository.get_employee_department_map({participation.employee_id})
        return self._to_participation_response(
            participation,
            employee_names.get(participation.employee_id),
            department_names.get(participation.employee_id),
        )

    def create_participation(
        self, payload: ParticipationCreate, user: AuthenticatedUser
    ) -> ParticipationResponse:
        if user.employee_id is None:
            raise BusinessRuleViolationError("Authenticated user has no employee profile")

        activity = self._repository.get_csr_activity(payload.csr_activity_id)
        validate_active_csr_activity(activity.status, activity.start_date, activity.end_date)
        self._repository.get_employee(user.employee_id)

        participation = EmployeeParticipation(
            employee_id=user.employee_id,
            csr_activity_id=payload.csr_activity_id,
            proof_file=payload.proof_file,
            approval_status=ApprovalStatus.PENDING,
        )
        created = self._repository.create_participation(participation)
        self._log_mutation(user, "CREATE", "employee_participation", created.id)
        self._db.commit()
        return self.get_participation(created.id)

    def update_participation(
        self, participation_id: UUID, payload: ParticipationUpdate, user: AuthenticatedUser
    ) -> ParticipationResponse:
        participation = self._repository.get_participation(participation_id)
        self._ensure_participation_owner_or_manager(participation, user)

        if participation.approval_status == ApprovalStatus.APPROVED:
            raise BusinessRuleViolationError("Approved participations cannot be modified")

        if payload.proof_file is not None:
            participation.proof_file = payload.proof_file

        updated = self._repository.update_participation(participation)
        self._log_mutation(user, "UPDATE", "employee_participation", updated.id)
        self._db.commit()
        return self.get_participation(updated.id)

    def approve_participation(
        self, participation_id: UUID, user: AuthenticatedUser
    ) -> ParticipationResponse:
        self._ensure_approver(user)
        participation = self._repository.get_participation(participation_id)
        activity = participation.csr_activity

        if participation.approval_status != ApprovalStatus.PENDING:
            raise BusinessRuleViolationError("Only pending participations can be approved")

        validate_approval_proof(
            activity.evidence_required,
            participation.proof_file,
            ApprovalStatus.APPROVED,
        )

        participation.approval_status = ApprovalStatus.APPROVED
        participation.points_earned = activity.points
        participation.completion_date = date.today()
        participation.rejection_reason = None
        updated = self._repository.update_participation(participation)
        self._log_mutation(user, "APPROVE", "employee_participation", updated.id)
        publish_csr_participation_approved(
            {
                "participation_id": str(updated.id),
                "employee_id": str(updated.employee_id),
                "points_earned": updated.points_earned,
            }
        )
        self._db.commit()
        return self.get_participation(updated.id)

    def reject_participation(
        self,
        participation_id: UUID,
        user: AuthenticatedUser,
        rejection_reason: str | None = None,
    ) -> ParticipationResponse:
        self._ensure_approver(user)
        participation = self._repository.get_participation(participation_id)

        if participation.approval_status != ApprovalStatus.PENDING:
            raise BusinessRuleViolationError("Only pending participations can be rejected")

        participation.approval_status = ApprovalStatus.REJECTED
        participation.points_earned = 0
        participation.completion_date = None
        participation.rejection_reason = rejection_reason
        updated = self._repository.update_participation(participation)
        self._log_mutation(user, "REJECT", "employee_participation", updated.id)
        publish_csr_participation_rejected(
            {
                "participation_id": str(updated.id),
                "employee_id": str(updated.employee_id),
            }
        )
        self._db.commit()
        return self.get_participation(updated.id)

    def delete_participation(self, participation_id: UUID, user: AuthenticatedUser) -> None:
        participation = self._repository.get_participation(participation_id)
        self._ensure_participation_owner_or_manager(participation, user)
        if participation.approval_status == ApprovalStatus.APPROVED and not user.has_permission(
            "csr:write"
        ):
            raise PermissionDeniedError("Approved participations require manager access to delete")
        self._repository.delete_participation(participation)
        self._log_mutation(user, "DELETE", "employee_participation", participation_id)
        self._db.commit()

    def get_analytics(self) -> SocialAnalyticsResponse:
        total_employees = self._repository.count_active_employees()
        approved = self._repository.count_participations_by_status(ApprovalStatus.APPROVED)
        pending = self._repository.count_participations_by_status(ApprovalStatus.PENDING)
        total_participations = approved + pending + self._repository.count_participations_by_status(
            ApprovalStatus.REJECTED
        )

        participation_rate = (
            (Decimal(approved) / Decimal(total_employees) * Decimal("100")).quantize(
                Decimal("0.01")
            )
            if total_employees > 0
            else Decimal("0")
        )

        active_activities = self._repository.count_csr_activities_by_status(
            CSRActivityStatus.ACTIVE
        )
        completed_activities = self._repository.count_csr_activities_by_status(
            CSRActivityStatus.COMPLETED
        )
        activity_completion_rate = (
            (
                Decimal(completed_activities)
                / Decimal(active_activities + completed_activities)
                * Decimal("100")
            ).quantize(Decimal("0.01"))
            if (active_activities + completed_activities) > 0
            else Decimal("0")
        )

        social_score = (
            participation_rate * Decimal("0.6") + activity_completion_rate * Decimal("0.4")
        ).quantize(Decimal("0.01"))

        dept_stats = self._repository.get_department_participation_stats()
        department_participation = [
            DepartmentParticipationItem(
                department_id=dept_id,
                department_name=name,
                participation_count=participation_count,
                approved_count=approved_count,
                participation_rate=(
                    (Decimal(approved_count) / Decimal(employee_count) * Decimal("100")).quantize(
                        Decimal("0.01")
                    )
                    if employee_count > 0
                    else Decimal("0")
                ),
            )
            for dept_id, name, employee_count, participation_count, approved_count in dept_stats
        ]

        monthly_trend = self._repository.get_monthly_csr_trend()
        monthly_csr_trend = [
            MonthlyCsrTrendPoint(
                month=month,
                participation_count=participation_count,
                approved_count=approved_count,
            )
            for month, participation_count, approved_count in monthly_trend
        ]

        top_departments = self._repository.get_top_participating_departments()
        top_participating_departments = [
            TopParticipatingDepartment(
                department_id=dept_id,
                department_name=name,
                approved_participations=approved_count,
                total_points=total_points,
            )
            for dept_id, name, approved_count, total_points in top_departments
        ]

        return SocialAnalyticsResponse(
            participation_rate=participation_rate,
            total_employees=total_employees,
            total_participations=total_participations,
            approved_participations=approved,
            pending_approvals=pending,
            social_score=social_score,
            department_participation=department_participation,
            monthly_csr_trend=monthly_csr_trend,
            top_participating_departments=top_participating_departments,
            active_csr_activities=active_activities,
            completed_csr_activities=completed_activities,
        )

    def get_social_score(self) -> Decimal:
        return self.get_analytics().social_score

    def _to_csr_activity_response(
        self,
        activity: CsrActivity,
        department_name: str | None,
        counts: dict[str, int],
    ) -> CsrActivityResponse:
        return CsrActivityResponse(
            id=activity.id,
            title=activity.title,
            category=activity.category,
            department_id=activity.department_id,
            department_name=department_name,
            description=activity.description,
            start_date=activity.start_date,
            end_date=activity.end_date,
            points=activity.points,
            evidence_required=activity.evidence_required,
            status=activity.status,
            participation_count=counts.get("total", 0),
            approved_count=counts.get("approved", 0),
            created_at=activity.created_at,
            updated_at=activity.updated_at,
        )

    def _to_participation_response(
        self,
        participation: EmployeeParticipation,
        employee_name: str | None,
        department_name: str | None,
    ) -> ParticipationResponse:
        activity = participation.csr_activity
        return ParticipationResponse(
            id=participation.id,
            employee_id=participation.employee_id,
            employee_name=employee_name,
            department_name=department_name,
            csr_activity_id=participation.csr_activity_id,
            csr_activity_title=activity.title if activity else None,
            proof_file=participation.proof_file,
            approval_status=participation.approval_status,
            points_earned=participation.points_earned,
            completion_date=participation.completion_date,
            rejection_reason=participation.rejection_reason,
            created_at=participation.created_at,
            updated_at=participation.updated_at,
        )

    def _ensure_approver(self, user: AuthenticatedUser) -> None:
        if not user.has_permission("csr:write"):
            raise PermissionDeniedError(
                "Only authorized approvers can manage participation approval"
            )

    def _ensure_participation_owner_or_manager(
        self, participation: EmployeeParticipation, user: AuthenticatedUser
    ) -> None:
        if user.has_permission("csr:write"):
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
