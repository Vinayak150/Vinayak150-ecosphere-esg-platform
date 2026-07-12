from datetime import date

from app.modules.social.models import ApprovalStatus, CSRActivityStatus
from app.shared.exceptions.base import BusinessRuleViolationError, ValidationError


def validate_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise ValidationError("End date must be on or after start date")


def validate_active_csr_activity(
    status: CSRActivityStatus,
    start_date: date,
    end_date: date,
    *,
    reference_date: date | None = None,
) -> None:
    today = reference_date or date.today()
    if status != CSRActivityStatus.ACTIVE:
        raise BusinessRuleViolationError("CSR activity is not active")
    if start_date > today:
        raise BusinessRuleViolationError("CSR activity has not started yet")
    if end_date < today:
        raise BusinessRuleViolationError("CSR activity has already ended")


def validate_approval_proof(
    evidence_required: bool,
    proof_file: str | None,
    approval_status: ApprovalStatus,
) -> None:
    if approval_status == ApprovalStatus.APPROVED and evidence_required and not proof_file:
        raise BusinessRuleViolationError(
            "Proof upload is required before approving this participation"
        )


def validate_positive_points(points: int) -> int:
    if points < 0:
        raise ValidationError("Points cannot be negative")
    return points
