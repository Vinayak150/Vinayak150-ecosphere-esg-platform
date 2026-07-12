from datetime import date
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.auth.models import Department, Employee
from app.modules.governance.models import (
    AcknowledgementStatus,
    Audit,
    AuditStatus,
    ComplianceIssue,
    ComplianceIssueStatus,
    ComplianceSeverity,
    Policy,
    PolicyAcknowledgement,
    PolicyStatus,
)
from app.modules.governance.schemas import GovernanceListParams
from app.shared.exceptions.base import ConflictError, NotFoundError
from app.shared.models.base import EntityStatus
from app.shared.pagination.pagination import calculate_pagination
from app.shared.validators.enums import parse_enum_value

_STATUS_ENUMS = {
    Policy: PolicyStatus,
    Audit: AuditStatus,
    ComplianceIssue: ComplianceIssueStatus,
}


class GovernanceRepository:
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

    def get_policy(self, policy_id: UUID) -> Policy:
        policy = self._db.get(Policy, policy_id)
        if policy is None:
            raise NotFoundError("Policy not found")
        return policy

    def get_audit(self, audit_id: UUID) -> Audit:
        audit = self._db.get(Audit, audit_id)
        if audit is None:
            raise NotFoundError("Audit not found")
        return audit

    def get_compliance_issue(self, issue_id: UUID) -> ComplianceIssue:
        issue = self._db.get(ComplianceIssue, issue_id)
        if issue is None:
            raise NotFoundError("Compliance issue not found")
        return issue

    def list_policies(
        self, params: GovernanceListParams
    ) -> tuple[list[Policy], dict[str, int]]:
        query = select(Policy)
        query = self._apply_common_filters(query, Policy, params)
        return self._paginate(query, params)

    def create_policy(self, policy: Policy) -> Policy:
        self._db.add(policy)
        self._db.flush()
        return policy

    def update_policy(self, policy: Policy) -> Policy:
        self._db.add(policy)
        self._db.flush()
        return policy

    def delete_policy(self, policy: Policy) -> None:
        self._db.delete(policy)
        self._db.flush()

    def list_audits(self, params: GovernanceListParams) -> tuple[list[Audit], dict[str, int]]:
        query = select(Audit)
        query = self._apply_common_filters(query, Audit, params)
        if params.department_id:
            query = query.where(Audit.department_id == params.department_id)
        return self._paginate(query, params)

    def create_audit(self, audit: Audit) -> Audit:
        self._db.add(audit)
        self._db.flush()
        return audit

    def update_audit(self, audit: Audit) -> Audit:
        self._db.add(audit)
        self._db.flush()
        return audit

    def delete_audit(self, audit: Audit) -> None:
        self._db.delete(audit)
        self._db.flush()

    def list_compliance_issues(
        self, params: GovernanceListParams
    ) -> tuple[list[ComplianceIssue], dict[str, int]]:
        query = select(ComplianceIssue)
        query = self._apply_common_filters(query, ComplianceIssue, params)
        if params.audit_id:
            query = query.where(ComplianceIssue.audit_id == params.audit_id)
        if params.owner_id:
            query = query.where(ComplianceIssue.owner_id == params.owner_id)
        if params.severity:
            severity = parse_enum_value(params.severity, ComplianceSeverity, field_name="severity")
            query = query.where(ComplianceIssue.severity == severity)
        return self._paginate(query, params)

    def create_compliance_issue(self, issue: ComplianceIssue) -> ComplianceIssue:
        self._db.add(issue)
        self._db.flush()
        return issue

    def update_compliance_issue(self, issue: ComplianceIssue) -> ComplianceIssue:
        self._db.add(issue)
        self._db.flush()
        return issue

    def delete_compliance_issue(self, issue: ComplianceIssue) -> None:
        self._db.delete(issue)
        self._db.flush()

    def list_acknowledgements(
        self, params: GovernanceListParams
    ) -> tuple[list[PolicyAcknowledgement], dict[str, int]]:
        query = select(PolicyAcknowledgement).options(
            joinedload(PolicyAcknowledgement.policy)
        )
        if params.policy_id:
            query = query.where(PolicyAcknowledgement.policy_id == params.policy_id)
        if params.employee_id:
            query = query.where(PolicyAcknowledgement.employee_id == params.employee_id)
        if params.status:
            status = parse_enum_value(params.status, AcknowledgementStatus)
            query = query.where(PolicyAcknowledgement.status == status)
        sort_column = getattr(
            PolicyAcknowledgement,
            params.sort or "created_at",
            PolicyAcknowledgement.created_at,
        )
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        query = query.order_by(ordering)
        return self._paginate(query, params)

    def get_acknowledgement_by_employee_policy(
        self, employee_id: UUID, policy_id: UUID
    ) -> PolicyAcknowledgement | None:
        stmt = select(PolicyAcknowledgement).where(
            PolicyAcknowledgement.employee_id == employee_id,
            PolicyAcknowledgement.policy_id == policy_id,
        )
        return self._db.scalars(stmt).first()

    def create_acknowledgement(
        self, acknowledgement: PolicyAcknowledgement
    ) -> PolicyAcknowledgement:
        existing = self.get_acknowledgement_by_employee_policy(
            acknowledgement.employee_id, acknowledgement.policy_id
        )
        if existing is not None:
            raise ConflictError("Policy already acknowledged by this employee")
        self._db.add(acknowledgement)
        self._db.flush()
        return acknowledgement

    def update_acknowledgement(
        self, acknowledgement: PolicyAcknowledgement
    ) -> PolicyAcknowledgement:
        self._db.add(acknowledgement)
        self._db.flush()
        return acknowledgement

    def sync_overdue_issues(self, today: date) -> int:
        stmt = select(ComplianceIssue).where(
            ComplianceIssue.due_date < today,
            ComplianceIssue.status.in_(
                [ComplianceIssueStatus.OPEN, ComplianceIssueStatus.IN_PROGRESS]
            ),
        )
        issues = self._db.scalars(stmt).all()
        for issue in issues:
            issue.status = ComplianceIssueStatus.OVERDUE
            self._db.add(issue)
        if issues:
            self._db.flush()
        return len(issues)

    def count_policies_by_status(self, status: PolicyStatus) -> int:
        return (
            self._db.scalar(
                select(func.count()).select_from(Policy).where(Policy.status == status)
            )
            or 0
        )

    def count_audits_by_status(self, status: AuditStatus) -> int:
        return (
            self._db.scalar(
                select(func.count()).select_from(Audit).where(Audit.status == status)
            )
            or 0
        )

    def count_issues_by_status(self, status: ComplianceIssueStatus) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(ComplianceIssue)
                .where(ComplianceIssue.status == status)
            )
            or 0
        )

    def count_open_issues(self) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(ComplianceIssue)
                .where(
                    ComplianceIssue.status.in_(
                        [
                            ComplianceIssueStatus.OPEN,
                            ComplianceIssueStatus.IN_PROGRESS,
                            ComplianceIssueStatus.OVERDUE,
                        ]
                    )
                )
            )
            or 0
        )

    def count_acknowledgements_by_status(self, status: AcknowledgementStatus) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(PolicyAcknowledgement)
                .where(PolicyAcknowledgement.status == status)
            )
            or 0
        )

    def count_total_employees(self) -> int:
        return (
            self._db.scalar(
                select(func.count())
                .select_from(Employee)
                .where(Employee.status == EntityStatus.ACTIVE)
            )
            or 0
        )

    def get_policy_ack_stats(self, policy_ids: set[UUID]) -> dict[UUID, dict[str, int]]:
        if not policy_ids:
            return {}
        rows = self._db.execute(
            select(
                PolicyAcknowledgement.policy_id,
                PolicyAcknowledgement.status,
                func.count(),
            )
            .where(PolicyAcknowledgement.policy_id.in_(policy_ids))
            .group_by(PolicyAcknowledgement.policy_id, PolicyAcknowledgement.status)
        ).all()
        stats: dict[UUID, dict[str, int]] = {}
        for policy_id, status, count in rows:
            entry = stats.setdefault(policy_id, {"total": 0, "acknowledged": 0, "pending": 0})
            entry["total"] += count
            if status == AcknowledgementStatus.ACKNOWLEDGED:
                entry["acknowledged"] += count
            else:
                entry["pending"] += count
        return stats

    def get_audit_issue_stats(self, audit_ids: set[UUID]) -> dict[UUID, dict[str, int]]:
        if not audit_ids:
            return {}
        rows = self._db.execute(
            select(
                ComplianceIssue.audit_id,
                ComplianceIssue.status,
                func.count(),
            )
            .where(ComplianceIssue.audit_id.in_(audit_ids))
            .group_by(ComplianceIssue.audit_id, ComplianceIssue.status)
        ).all()
        stats: dict[UUID, dict[str, int]] = {}
        for audit_id, status, count in rows:
            if audit_id is None:
                continue
            entry = stats.setdefault(audit_id, {"total": 0, "open": 0})
            entry["total"] += count
            if status != ComplianceIssueStatus.CLOSED:
                entry["open"] += count
        return stats

    def list_departments(self) -> list[Department]:
        stmt = (
            select(Department)
            .where(Department.status == EntityStatus.ACTIVE)
            .order_by(Department.name)
        )
        return list(self._db.scalars(stmt).all())

    def list_active_employees(self) -> list[Employee]:
        stmt = (
            select(Employee)
            .where(Employee.status == EntityStatus.ACTIVE)
            .order_by(Employee.first_name, Employee.last_name)
        )
        return list(self._db.scalars(stmt).all())

    def get_department_name_map(self, department_ids: set[UUID]) -> dict[UUID, str]:
        if not department_ids:
            return {}
        rows = self._db.execute(
            select(Department.id, Department.name).where(Department.id.in_(department_ids))
        ).all()
        return {row[0]: row[1] for row in rows}

    def get_employee_name_map(self, employee_ids: set[UUID]) -> dict[UUID, str]:
        if not employee_ids:
            return {}
        rows = self._db.execute(
            select(Employee.id, Employee.first_name, Employee.last_name).where(
                Employee.id.in_(employee_ids)
            )
        ).all()
        return {row[0]: f"{row[1]} {row[2]}" for row in rows}

    def get_policy_title_map(self, policy_ids: set[UUID]) -> dict[UUID, str]:
        if not policy_ids:
            return {}
        rows = self._db.execute(
            select(Policy.id, Policy.title).where(Policy.id.in_(policy_ids))
        ).all()
        return {row[0]: row[1] for row in rows}

    def get_audit_title_map(self, audit_ids: set[UUID]) -> dict[UUID, str]:
        if not audit_ids:
            return {}
        rows = self._db.execute(
            select(Audit.id, Audit.title).where(Audit.id.in_(audit_ids))
        ).all()
        return {row[0]: row[1] for row in rows}

    def _apply_common_filters(
        self, query: Select, model, params: GovernanceListParams
    ) -> Select:
        if params.search and hasattr(model, "title"):
            query = query.where(model.title.ilike(f"%{params.search}%"))
        if params.status and hasattr(model, "status"):
            status_enum = _STATUS_ENUMS.get(model)
            if status_enum is not None:
                status = parse_enum_value(params.status, status_enum)
                query = query.where(model.status == status)
        sort_column = getattr(model, params.sort or "created_at", model.created_at)
        ordering = asc(sort_column) if params.order == "asc" else desc(sort_column)
        return query.order_by(ordering)

    def _paginate(self, query: Select, params: GovernanceListParams) -> tuple[list, dict]:
        total = self._db.scalar(select(func.count()).select_from(query.subquery())) or 0
        pagination = calculate_pagination(params.page, params.page_size, total)
        items = list(
            self._db.scalars(
                query.offset((params.page - 1) * params.page_size).limit(params.page_size)
            ).all()
        )
        return items, pagination
