from datetime import date

from app.modules.governance.models import ComplianceIssueStatus, PolicyStatus
from app.modules.governance.schemas import (
    ComplianceIssueCreate,
    PolicyCreate,
)
from app.shared.exceptions.base import BusinessRuleViolationError, ValidationError


def validate_policy_effective_date(effective_date: date) -> None:
    if effective_date < date(2000, 1, 1):
        raise ValidationError("Effective date is invalid")


def validate_compliance_issue_required_fields(payload: ComplianceIssueCreate) -> None:
    if payload.owner_id is None:
        raise ValidationError("Compliance issue must have an owner")
    if payload.due_date is None:
        raise ValidationError("Compliance issue must have a due date")
    if payload.severity is None:
        raise ValidationError("Compliance issue must have a severity")
    if not payload.description.strip():
        raise ValidationError("Compliance issue must have a description")


def validate_compliance_issue_update(
    updates: dict, current_status: ComplianceIssueStatus
) -> None:
    if current_status == ComplianceIssueStatus.CLOSED:
        raise BusinessRuleViolationError("Closed compliance issues cannot be modified")
    if "owner_id" in updates and updates["owner_id"] is None:
        raise ValidationError("Compliance issue must have an owner")
    if "due_date" in updates and updates["due_date"] is None:
        raise ValidationError("Compliance issue must have a due date")
    if "severity" in updates and updates["severity"] is None:
        raise ValidationError("Compliance issue must have a severity")


def validate_active_policy_for_acknowledgement(status: PolicyStatus) -> None:
    if status != PolicyStatus.ACTIVE:
        raise BusinessRuleViolationError("Only active policies can be acknowledged")


def validate_policy_create(payload: PolicyCreate) -> None:
    validate_policy_effective_date(payload.effective_date)
