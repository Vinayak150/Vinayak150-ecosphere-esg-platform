from uuid import UUID

from sqlalchemy import Select, asc, case, desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.auth.models import Department, Employee
from app.modules.social.models import (
    ApprovalStatus,
    CsrActivity,
    CSRActivityStatus,
    EmployeeParticipation,
)
from app.modules.social.schemas import SocialListParams
from app.shared.exceptions.base import ConflictError, NotFoundError
from app.shared.models.base import EntityStatus
from app.shared.pagination.pagination import calculate_pagination
from app.shared.validators.enums import parse_enum_value


class SocialRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_department(self, department_id: UUID) -> Department:
        department = self._db.get(Department, department_id)
        if department is None or department.status != EntityStatus.ACTIVE:
            raise NotFoundError("Department not found")
        return department

    def get_employee(self, employee_id: UUID) -> Employee:
        employee = self._db.get(Employee, employee_id)
        if employee is None or employee.status != EntityStatus.ACTIVE:
            raise NotFoundError("Employee not found")
        return employee

    def get_csr_activity(self, activity_id: UUID) -> CsrActivity:
        activity = self._db.get(CsrActivity, activity_id)
        if activity is None:
            raise NotFoundError("CSR activity not found")
        return activity

    def list_csr_activities(
        self, params: SocialListParams
    ) -> tuple[list[CsrActivity], dict[str, int]]:
        query = select(CsrActivity)
        query = self._apply_common_filters(query, CsrActivity, params)
        if params.department_id:
            query = query.where(CsrActivity.department_id == params.department_id)
        if params.category:
            query = query.where(CsrActivity.category.ilike(f"%{params.category}%"))
        return self._paginate(query, params)

    def create_csr_activity(self, activity: CsrActivity) -> CsrActivity:
        self._db.add(activity)
        self._db.flush()
        return activity

    def update_csr_activity(self, activity: CsrActivity) -> CsrActivity:
        self._db.add(activity)
        self._db.flush()
        return activity

    def delete_csr_activity(self, activity: CsrActivity) -> None:
        self._db.delete(activity)
        self._db.flush()

    def get_participation(self, participation_id: UUID) -> EmployeeParticipation:
        stmt = (
            select(EmployeeParticipation)
            .options(joinedload(EmployeeParticipation.csr_activity))
            .where(EmployeeParticipation.id == participation_id)
        )
        participation = self._db.scalars(stmt).first()
        if participation is None:
            raise NotFoundError("Participation record not found")
        return participation

    def get_participation_by_employee_activity(
        self, employee_id: UUID, csr_activity_id: UUID
    ) -> EmployeeParticipation | None:
        stmt = select(EmployeeParticipation).where(
            EmployeeParticipation.employee_id == employee_id,
            EmployeeParticipation.csr_activity_id == csr_activity_id,
        )
        return self._db.scalars(stmt).first()

    def list_participations(
        self, params: SocialListParams
    ) -> tuple[list[EmployeeParticipation], dict[str, int]]:
        query = select(EmployeeParticipation).options(
            joinedload(EmployeeParticipation.csr_activity)
        )
        if params.approval_status:
            approval = parse_enum_value(
                params.approval_status, ApprovalStatus, field_name="approval_status"
            )
            query = query.where(EmployeeParticipation.approval_status == approval)
        if params.csr_activity_id:
            query = query.where(EmployeeParticipation.csr_activity_id == params.csr_activity_id)
        if params.employee_id:
            query = query.where(EmployeeParticipation.employee_id == params.employee_id)
        if params.search:
            query = query.join(CsrActivity).where(CsrActivity.title.ilike(f"%{params.search}%"))
        sort_column = getattr(
            EmployeeParticipation, params.sort or "created_at", EmployeeParticipation.created_at
        )
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        query = query.order_by(ordering)
        return self._paginate(query, params)

    def create_participation(self, participation: EmployeeParticipation) -> EmployeeParticipation:
        existing = self.get_participation_by_employee_activity(
            participation.employee_id, participation.csr_activity_id
        )
        if existing is not None:
            raise ConflictError("Employee has already joined this CSR activity")
        self._db.add(participation)
        self._db.flush()
        return participation

    def update_participation(self, participation: EmployeeParticipation) -> EmployeeParticipation:
        self._db.add(participation)
        self._db.flush()
        return participation

    def delete_participation(self, participation: EmployeeParticipation) -> None:
        self._db.delete(participation)
        self._db.flush()

    def get_department_name_map(self, department_ids: set[UUID]) -> dict[UUID, str]:
        if not department_ids:
            return {}
        stmt = select(Department.id, Department.name).where(Department.id.in_(department_ids))
        return {row.id: row.name for row in self._db.execute(stmt).all()}

    def get_employee_name_map(self, employee_ids: set[UUID]) -> dict[UUID, str]:
        if not employee_ids:
            return {}
        stmt = select(Employee.id, Employee.first_name, Employee.last_name).where(
            Employee.id.in_(employee_ids)
        )
        return {row.id: f"{row.first_name} {row.last_name}" for row in self._db.execute(stmt).all()}

    def get_employee_department_map(self, employee_ids: set[UUID]) -> dict[UUID, str | None]:
        if not employee_ids:
            return {}
        stmt = (
            select(Employee.id, Department.name)
            .outerjoin(Department, Employee.department_id == Department.id)
            .where(Employee.id.in_(employee_ids))
        )
        return {row.id: row.name for row in self._db.execute(stmt).all()}

    def count_active_employees(self) -> int:
        stmt = (
            select(func.count())
            .select_from(Employee)
            .where(Employee.status == EntityStatus.ACTIVE)
        )
        return int(self._db.scalar(stmt) or 0)

    def count_participations_by_status(self, status: ApprovalStatus) -> int:
        stmt = (
            select(func.count())
            .select_from(EmployeeParticipation)
            .where(EmployeeParticipation.approval_status == status)
        )
        return int(self._db.scalar(stmt) or 0)

    def count_csr_activities_by_status(self, status: CSRActivityStatus) -> int:
        stmt = (
            select(func.count())
            .select_from(CsrActivity)
            .where(CsrActivity.status == status)
        )
        return int(self._db.scalar(stmt) or 0)

    def get_participation_counts_for_activities(
        self, activity_ids: set[UUID]
    ) -> dict[UUID, dict[str, int]]:
        if not activity_ids:
            return {}
        stmt = (
            select(
                EmployeeParticipation.csr_activity_id,
                EmployeeParticipation.approval_status,
                func.count(),
            )
            .where(EmployeeParticipation.csr_activity_id.in_(activity_ids))
            .group_by(EmployeeParticipation.csr_activity_id, EmployeeParticipation.approval_status)
        )
        result: dict[UUID, dict[str, int]] = {}
        for activity_id, approval_status, count in self._db.execute(stmt).all():
            entry = result.setdefault(activity_id, {"total": 0, "approved": 0})
            entry["total"] += int(count)
            if approval_status == ApprovalStatus.APPROVED:
                entry["approved"] = int(count)
        return result

    def get_department_participation_stats(self) -> list[tuple[UUID, str, int, int, int]]:
        return self._get_department_participation_stats()

    def _get_department_participation_stats(
        self,
    ) -> list[tuple[UUID, str, int, int, int]]:
        departments = list(
            self._db.scalars(
                select(Department).where(Department.status == EntityStatus.ACTIVE)
            ).all()
        )
        results: list[tuple[UUID, str, int, int, int]] = []
        for department in departments:
            employee_count = int(
                self._db.scalar(
                    select(func.count())
                    .select_from(Employee)
                    .where(
                        Employee.department_id == department.id,
                        Employee.status == EntityStatus.ACTIVE,
                    )
                )
                or 0
            )
            participation_count = int(
                self._db.scalar(
                    select(func.count())
                    .select_from(EmployeeParticipation)
                    .join(Employee, EmployeeParticipation.employee_id == Employee.id)
                    .where(Employee.department_id == department.id)
                )
                or 0
            )
            approved_count = int(
                self._db.scalar(
                    select(func.count())
                    .select_from(EmployeeParticipation)
                    .join(Employee, EmployeeParticipation.employee_id == Employee.id)
                    .where(
                        Employee.department_id == department.id,
                        EmployeeParticipation.approval_status == ApprovalStatus.APPROVED,
                    )
                )
                or 0
            )
            results.append(
                (
                    department.id,
                    department.name,
                    employee_count,
                    participation_count,
                    approved_count,
                )
            )
        return results

    def get_monthly_csr_trend(self) -> list[tuple[str, int, int]]:
        month_label = func.to_char(EmployeeParticipation.created_at, "YYYY-MM")
        approved_case = func.sum(
            case(
                (EmployeeParticipation.approval_status == ApprovalStatus.APPROVED, 1),
                else_=0,
            )
        )
        stmt = (
            select(
                month_label,
                func.count(EmployeeParticipation.id),
                func.coalesce(approved_case, 0),
            )
            .group_by(month_label)
            .order_by(month_label)
        )
        return [(row[0], int(row[1]), int(row[2])) for row in self._db.execute(stmt).all()]

    def get_top_participating_departments(self, limit: int = 5) -> list[tuple[UUID, str, int, int]]:
        stmt = (
            select(
                Department.id,
                Department.name,
                func.count(EmployeeParticipation.id),
                func.coalesce(func.sum(EmployeeParticipation.points_earned), 0),
            )
            .join(Employee, Employee.department_id == Department.id)
            .join(EmployeeParticipation, EmployeeParticipation.employee_id == Employee.id)
            .where(EmployeeParticipation.approval_status == ApprovalStatus.APPROVED)
            .group_by(Department.id, Department.name)
            .order_by(desc(func.count(EmployeeParticipation.id)))
            .limit(limit)
        )
        return [(row[0], row[1], int(row[2]), int(row[3])) for row in self._db.execute(stmt).all()]

    def list_active_employees(self) -> list[Employee]:
        stmt = (
            select(Employee)
            .where(Employee.status == EntityStatus.ACTIVE)
            .order_by(Employee.first_name, Employee.last_name)
        )
        return list(self._db.scalars(stmt).all())

    def list_departments(self) -> list[Department]:
        stmt = (
            select(Department)
            .where(Department.status == EntityStatus.ACTIVE)
            .order_by(Department.name)
        )
        return list(self._db.scalars(stmt).all())

    def _apply_common_filters(self, query: Select, model, params: SocialListParams) -> Select:
        if params.search and hasattr(model, "title"):
            query = query.where(model.title.ilike(f"%{params.search}%"))
        if params.status and hasattr(model, "status"):
            status = parse_enum_value(params.status, CSRActivityStatus)
            query = query.where(model.status == status)
        sort_column = getattr(model, params.sort or "created_at", model.created_at)
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        return query.order_by(ordering)

    def _paginate(self, query: Select, params: SocialListParams) -> tuple[list, dict[str, int]]:
        total = self._db.scalar(select(func.count()).select_from(query.subquery())) or 0
        offset = (params.page - 1) * params.page_size
        items = list(self._db.scalars(query.offset(offset).limit(params.page_size)).all())
        return items, calculate_pagination(params.page, params.page_size, total)
