from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.schemas import AuthenticatedUser
from app.modules.governance.events import (
    publish_audit_completed,
    publish_compliance_issue_closed,
    publish_compliance_issue_raised,
    publish_policy_acknowledged,
)
from app.modules.governance.models import (
    AcknowledgementStatus,
    Audit,
    AuditStatus,
    ComplianceIssue,
    ComplianceIssueStatus,
    Policy,
    PolicyAcknowledgement,
    PolicyStatus,
)
from app.modules.governance.repository import GovernanceRepository
from app.modules.governance.schemas import (
    AuditCreate,
    AuditResponse,
    AuditUpdate,
    ComplianceIssueCreate,
    ComplianceIssueResponse,
    ComplianceIssueUpdate,
    EmployeeOption,
    GovernanceAnalyticsResponse,
    GovernanceListParams,
    PolicyAcknowledgementCreate,
    PolicyAcknowledgementResponse,
    PolicyCreate,
    PolicyResponse,
    PolicyUpdate,
)
from app.modules.governance.validators import (
    validate_active_policy_for_acknowledgement,
    validate_compliance_issue_required_fields,
    validate_compliance_issue_update,
    validate_policy_create,
)
from app.shared.exceptions.base import BusinessRuleViolationError, PermissionDeniedError
from app.shared.services.activity_log import ActivityLogService


class GovernanceService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repository = GovernanceRepository(db)
        self._activity_log = ActivityLogService(db)

    def list_departments(self) -> list[dict[str, str]]:
        departments = self._repository.list_departments()
        return [{"id": str(d.id), "name": d.name, "code": d.code} for d in departments]

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

    def list_policies(
        self, params: GovernanceListParams
    ) -> tuple[list[PolicyResponse], dict[str, int]]:
        items, pagination = self._repository.list_policies(params)
        policy_ids = {item.id for item in items}
        stats = self._repository.get_policy_ack_stats(policy_ids)
        return [
            self._to_policy_response(item, stats.get(item.id, {"total": 0, "pending": 0}))
            for item in items
        ], pagination

    def get_policy(self, policy_id: UUID) -> PolicyResponse:
        policy = self._repository.get_policy(policy_id)
        stats = self._repository.get_policy_ack_stats({policy.id})
        return self._to_policy_response(
            policy, stats.get(policy.id, {"total": 0, "pending": 0})
        )

    def create_policy(self, payload: PolicyCreate, user: AuthenticatedUser) -> PolicyResponse:
        validate_policy_create(payload)
        policy = Policy(**payload.model_dump())
        created = self._repository.create_policy(policy)
        self._log_mutation(user, "CREATE", "policy", created.id)
        self._db.commit()
        return self.get_policy(created.id)

    def update_policy(
        self, policy_id: UUID, payload: PolicyUpdate, user: AuthenticatedUser
    ) -> PolicyResponse:
        policy = self._repository.get_policy(policy_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(policy, field, value)
        updated = self._repository.update_policy(policy)
        self._log_mutation(user, "UPDATE", "policy", updated.id)
        self._db.commit()
        return self.get_policy(updated.id)

    def delete_policy(self, policy_id: UUID, user: AuthenticatedUser) -> None:
        policy = self._repository.get_policy(policy_id)
        self._repository.delete_policy(policy)
        self._log_mutation(user, "DELETE", "policy", policy_id)
        self._db.commit()

    def list_audits(
        self, params: GovernanceListParams
    ) -> tuple[list[AuditResponse], dict[str, int]]:
        items, pagination = self._repository.list_audits(params)
        audit_ids = {item.id for item in items}
        department_ids = {item.department_id for item in items}
        auditor_ids = {item.auditor_id for item in items}
        department_names = self._repository.get_department_name_map(department_ids)
        auditor_names = self._repository.get_employee_name_map(auditor_ids)
        issue_stats = self._repository.get_audit_issue_stats(audit_ids)
        return [
            self._to_audit_response(
                item,
                department_names.get(item.department_id),
                auditor_names.get(item.auditor_id),
                issue_stats.get(item.id, {"total": 0, "open": 0}),
            )
            for item in items
        ], pagination

    def get_audit(self, audit_id: UUID) -> AuditResponse:
        audit = self._repository.get_audit(audit_id)
        department_names = self._repository.get_department_name_map({audit.department_id})
        auditor_names = self._repository.get_employee_name_map({audit.auditor_id})
        issue_stats = self._repository.get_audit_issue_stats({audit.id})
        return self._to_audit_response(
            audit,
            department_names.get(audit.department_id),
            auditor_names.get(audit.auditor_id),
            issue_stats.get(audit.id, {"total": 0, "open": 0}),
        )

    def create_audit(self, payload: AuditCreate, user: AuthenticatedUser) -> AuditResponse:
        self._repository.get_department(payload.department_id)
        self._repository.get_employee(payload.auditor_id)
        audit = Audit(**payload.model_dump())
        created = self._repository.create_audit(audit)
        self._log_mutation(user, "CREATE", "audit", created.id)
        self._db.commit()
        return self.get_audit(created.id)

    def update_audit(
        self, audit_id: UUID, payload: AuditUpdate, user: AuthenticatedUser
    ) -> AuditResponse:
        audit = self._repository.get_audit(audit_id)
        updates = payload.model_dump(exclude_unset=True)
        if "department_id" in updates and updates["department_id"] is not None:
            self._repository.get_department(updates["department_id"])
        if "auditor_id" in updates and updates["auditor_id"] is not None:
            self._repository.get_employee(updates["auditor_id"])

        previous_status = audit.status
        for field, value in updates.items():
            setattr(audit, field, value)

        updated = self._repository.update_audit(audit)
        self._log_mutation(user, "UPDATE", "audit", updated.id)
        if (
            updated.status == AuditStatus.COMPLETED
            and previous_status != AuditStatus.COMPLETED
        ):
            publish_audit_completed(
                {"audit_id": str(updated.id), "title": updated.title}
            )
        self._db.commit()
        return self.get_audit(updated.id)

    def delete_audit(self, audit_id: UUID, user: AuthenticatedUser) -> None:
        audit = self._repository.get_audit(audit_id)
        self._repository.delete_audit(audit)
        self._log_mutation(user, "DELETE", "audit", audit_id)
        self._db.commit()

    def list_compliance_issues(
        self, params: GovernanceListParams
    ) -> tuple[list[ComplianceIssueResponse], dict[str, int]]:
        self._repository.sync_overdue_issues(date.today())
        items, pagination = self._repository.list_compliance_issues(params)
        owner_ids = {item.owner_id for item in items}
        audit_ids = {item.audit_id for item in items if item.audit_id}
        owner_names = self._repository.get_employee_name_map(owner_ids)
        audit_titles = self._repository.get_audit_title_map(audit_ids)
        return [
            self._to_compliance_issue_response(
                item,
                owner_names.get(item.owner_id),
                audit_titles.get(item.audit_id) if item.audit_id else None,
            )
            for item in items
        ], pagination

    def get_compliance_issue(self, issue_id: UUID) -> ComplianceIssueResponse:
        self._repository.sync_overdue_issues(date.today())
        issue = self._repository.get_compliance_issue(issue_id)
        owner_names = self._repository.get_employee_name_map({issue.owner_id})
        audit_titles = (
            self._repository.get_audit_title_map({issue.audit_id})
            if issue.audit_id
            else {}
        )
        return self._to_compliance_issue_response(
            issue,
            owner_names.get(issue.owner_id),
            audit_titles.get(issue.audit_id) if issue.audit_id else None,
        )

    def create_compliance_issue(
        self, payload: ComplianceIssueCreate, user: AuthenticatedUser
    ) -> ComplianceIssueResponse:
        validate_compliance_issue_required_fields(payload)
        self._repository.get_employee(payload.owner_id)
        if payload.audit_id is not None:
            self._repository.get_audit(payload.audit_id)
        issue = ComplianceIssue(**payload.model_dump())
        created = self._repository.create_compliance_issue(issue)
        self._log_mutation(user, "CREATE", "compliance_issue", created.id)
        publish_compliance_issue_raised(
            {
                "issue_id": str(created.id),
                "severity": created.severity.value,
                "owner_id": str(created.owner_id),
            }
        )
        self._db.commit()
        return self.get_compliance_issue(created.id)

    def update_compliance_issue(
        self, issue_id: UUID, payload: ComplianceIssueUpdate, user: AuthenticatedUser
    ) -> ComplianceIssueResponse:
        issue = self._repository.get_compliance_issue(issue_id)
        updates = payload.model_dump(exclude_unset=True)
        validate_compliance_issue_update(updates, issue.status)
        if "owner_id" in updates and updates["owner_id"] is not None:
            self._repository.get_employee(updates["owner_id"])
        if "audit_id" in updates and updates["audit_id"] is not None:
            self._repository.get_audit(updates["audit_id"])

        for field, value in updates.items():
            setattr(issue, field, value)

        updated = self._repository.update_compliance_issue(issue)
        self._log_mutation(user, "UPDATE", "compliance_issue", updated.id)
        self._db.commit()
        return self.get_compliance_issue(updated.id)

    def close_compliance_issue(
        self, issue_id: UUID, user: AuthenticatedUser
    ) -> ComplianceIssueResponse:
        issue = self._repository.get_compliance_issue(issue_id)
        if issue.status == ComplianceIssueStatus.CLOSED:
            raise BusinessRuleViolationError("Compliance issue is already closed")
        issue.status = ComplianceIssueStatus.CLOSED
        updated = self._repository.update_compliance_issue(issue)
        self._log_mutation(user, "CLOSE", "compliance_issue", updated.id)
        publish_compliance_issue_closed(
            {"issue_id": str(updated.id), "owner_id": str(updated.owner_id)}
        )
        self._db.commit()
        return self.get_compliance_issue(updated.id)

    def delete_compliance_issue(self, issue_id: UUID, user: AuthenticatedUser) -> None:
        issue = self._repository.get_compliance_issue(issue_id)
        self._repository.delete_compliance_issue(issue)
        self._log_mutation(user, "DELETE", "compliance_issue", issue_id)
        self._db.commit()

    def list_acknowledgements(
        self, params: GovernanceListParams
    ) -> tuple[list[PolicyAcknowledgementResponse], dict[str, int]]:
        items, pagination = self._repository.list_acknowledgements(params)
        employee_ids = {item.employee_id for item in items}
        policy_ids = {item.policy_id for item in items}
        employee_names = self._repository.get_employee_name_map(employee_ids)
        policy_titles = self._repository.get_policy_title_map(policy_ids)
        return [
            self._to_acknowledgement_response(
                item,
                employee_names.get(item.employee_id),
                policy_titles.get(item.policy_id),
            )
            for item in items
        ], pagination

    def acknowledge_policy(
        self, payload: PolicyAcknowledgementCreate, user: AuthenticatedUser
    ) -> PolicyAcknowledgementResponse:
        if user.employee_id is None:
            raise PermissionDeniedError("Employee profile required to acknowledge policies")
        policy = self._repository.get_policy(payload.policy_id)
        validate_active_policy_for_acknowledgement(policy.status)

        existing = self._repository.get_acknowledgement_by_employee_policy(
            user.employee_id, payload.policy_id
        )
        if existing is not None and existing.status == AcknowledgementStatus.ACKNOWLEDGED:
            return self._to_acknowledgement_response(
                existing,
                None,
                policy.title,
            )

        if existing is not None:
            existing.status = AcknowledgementStatus.ACKNOWLEDGED
            existing.acknowledged_at = datetime.now(UTC)
            acknowledgement = self._repository.update_acknowledgement(existing)
        else:
            acknowledgement = PolicyAcknowledgement(
                employee_id=user.employee_id,
                policy_id=payload.policy_id,
                status=AcknowledgementStatus.ACKNOWLEDGED,
                acknowledged_at=datetime.now(UTC),
            )
            acknowledgement = self._repository.create_acknowledgement(acknowledgement)

        self._log_mutation(user, "ACKNOWLEDGE", "policy_acknowledgement", acknowledgement.id)
        publish_policy_acknowledged(
            {
                "policy_id": str(policy.id),
                "employee_id": str(user.employee_id),
                "title": policy.title,
            }
        )
        self._db.commit()
        employee_names = self._repository.get_employee_name_map({user.employee_id})
        return self._to_acknowledgement_response(
            acknowledgement,
            employee_names.get(user.employee_id),
            policy.title,
        )

    def get_analytics(self) -> GovernanceAnalyticsResponse:
        self._repository.sync_overdue_issues(date.today())

        total_policies = self._repository.count_policies_by_status(PolicyStatus.ACTIVE) + (
            self._repository.count_policies_by_status(PolicyStatus.INACTIVE)
            + self._repository.count_policies_by_status(PolicyStatus.ARCHIVED)
        )
        active_policies = self._repository.count_policies_by_status(PolicyStatus.ACTIVE)
        total_acknowledgements = (
            self._repository.count_acknowledgements_by_status(
                AcknowledgementStatus.ACKNOWLEDGED
            )
            + self._repository.count_acknowledgements_by_status(
                AcknowledgementStatus.PENDING
            )
        )
        acknowledged_count = self._repository.count_acknowledgements_by_status(
            AcknowledgementStatus.ACKNOWLEDGED
        )
        pending_acknowledgements = self._repository.count_acknowledgements_by_status(
            AcknowledgementStatus.PENDING
        )

        total_employees = self._repository.count_total_employees()
        expected_acknowledgements = active_policies * total_employees
        policy_completion = (
            (Decimal(acknowledged_count) / Decimal(expected_acknowledgements) * Decimal("100"))
            .quantize(Decimal("0.01"))
            if expected_acknowledgements > 0
            else Decimal("100")
            if active_policies == 0
            else Decimal("0")
        )

        total_issues = (
            self._repository.count_issues_by_status(ComplianceIssueStatus.OPEN)
            + self._repository.count_issues_by_status(ComplianceIssueStatus.IN_PROGRESS)
            + self._repository.count_issues_by_status(ComplianceIssueStatus.OVERDUE)
            + self._repository.count_issues_by_status(ComplianceIssueStatus.CLOSED)
        )
        closed_issues = self._repository.count_issues_by_status(ComplianceIssueStatus.CLOSED)
        open_issues = self._repository.count_open_issues()
        overdue_issues = self._repository.count_issues_by_status(ComplianceIssueStatus.OVERDUE)

        compliance_rate = (
            (Decimal(closed_issues) / Decimal(total_issues) * Decimal("100")).quantize(
                Decimal("0.01")
            )
            if total_issues > 0
            else Decimal("100")
        )

        total_audits = sum(
            self._repository.count_audits_by_status(status)
            for status in AuditStatus
        )
        completed_audits = self._repository.count_audits_by_status(AuditStatus.COMPLETED)
        audit_completion_rate = (
            (Decimal(completed_audits) / Decimal(total_audits) * Decimal("100")).quantize(
                Decimal("0.01")
            )
            if total_audits > 0
            else Decimal("100")
        )

        governance_score = (
            policy_completion * Decimal("0.35")
            + compliance_rate * Decimal("0.35")
            + audit_completion_rate * Decimal("0.30")
        ).quantize(Decimal("0.01"))

        return GovernanceAnalyticsResponse(
            governance_score=governance_score,
            compliance_rate=compliance_rate,
            open_issues=open_issues,
            overdue_issues=overdue_issues,
            policy_completion=policy_completion,
            total_policies=total_policies,
            active_policies=active_policies,
            total_acknowledgements=total_acknowledgements,
            acknowledged_count=acknowledged_count,
            pending_acknowledgements=pending_acknowledgements,
            total_audits=total_audits,
            completed_audits=completed_audits,
            closed_issues=closed_issues,
            total_issues=total_issues,
        )

    def get_governance_score(self) -> Decimal:
        return self.get_analytics().governance_score

    def _to_policy_response(self, policy: Policy, stats: dict[str, int]) -> PolicyResponse:
        return PolicyResponse(
            id=policy.id,
            title=policy.title,
            version=policy.version,
            description=policy.description,
            effective_date=policy.effective_date,
            status=policy.status,
            acknowledgement_count=stats.get("total", 0),
            pending_acknowledgements=stats.get("pending", 0),
            created_at=policy.created_at,
            updated_at=policy.updated_at,
        )

    def _to_audit_response(
        self,
        audit: Audit,
        department_name: str | None,
        auditor_name: str | None,
        issue_stats: dict[str, int],
    ) -> AuditResponse:
        return AuditResponse(
            id=audit.id,
            department_id=audit.department_id,
            department_name=department_name,
            title=audit.title,
            auditor_id=audit.auditor_id,
            auditor_name=auditor_name,
            audit_date=audit.audit_date,
            status=audit.status,
            issue_count=issue_stats.get("total", 0),
            open_issue_count=issue_stats.get("open", 0),
            created_at=audit.created_at,
            updated_at=audit.updated_at,
        )

    def _to_compliance_issue_response(
        self,
        issue: ComplianceIssue,
        owner_name: str | None,
        audit_title: str | None,
    ) -> ComplianceIssueResponse:
        today = date.today()
        is_overdue = issue.status == ComplianceIssueStatus.OVERDUE or (
            issue.status in (ComplianceIssueStatus.OPEN, ComplianceIssueStatus.IN_PROGRESS)
            and issue.due_date < today
        )
        return ComplianceIssueResponse(
            id=issue.id,
            audit_id=issue.audit_id,
            audit_title=audit_title,
            owner_id=issue.owner_id,
            owner_name=owner_name,
            severity=issue.severity,
            description=issue.description,
            due_date=issue.due_date,
            status=issue.status,
            is_overdue=is_overdue,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
        )

    def _to_acknowledgement_response(
        self,
        acknowledgement: PolicyAcknowledgement,
        employee_name: str | None,
        policy_title: str | None,
    ) -> PolicyAcknowledgementResponse:
        return PolicyAcknowledgementResponse(
            id=acknowledgement.id,
            employee_id=acknowledgement.employee_id,
            employee_name=employee_name,
            policy_id=acknowledgement.policy_id,
            policy_title=policy_title,
            acknowledged_at=acknowledgement.acknowledged_at,
            status=acknowledgement.status,
            created_at=acknowledgement.created_at,
            updated_at=acknowledgement.updated_at,
        )

    def _log_mutation(
        self, user: AuthenticatedUser, action: str, entity: str, entity_id: UUID
    ) -> None:
        self._activity_log.log_mutation(
            employee_id=user.employee_id,
            user_id=user.id,
            action=action,
            entity=entity,
            entity_id=entity_id,
        )
