from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.governance.models import (
    AcknowledgementStatus,
    AuditStatus,
    ComplianceIssueStatus,
    ComplianceSeverity,
    PolicyStatus,
)
from app.shared.schemas.responses import PaginationParams


class GovernanceListParams(PaginationParams):
    status: str | None = None
    department_id: UUID | None = None
    policy_id: UUID | None = None
    employee_id: UUID | None = None
    audit_id: UUID | None = None
    owner_id: UUID | None = None
    severity: str | None = None


class PolicyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    version: str = Field(min_length=1, max_length=50)
    description: str | None = None
    effective_date: date
    status: PolicyStatus = PolicyStatus.ACTIVE


class PolicyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    version: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    effective_date: date | None = None
    status: PolicyStatus | None = None


class PolicyResponse(BaseModel):
    id: UUID
    title: str
    version: str
    description: str | None
    effective_date: date
    status: PolicyStatus
    acknowledgement_count: int = 0
    pending_acknowledgements: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyAcknowledgementCreate(BaseModel):
    policy_id: UUID


class PolicyAcknowledgementResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: str | None = None
    policy_id: UUID
    policy_title: str | None = None
    acknowledged_at: datetime | None
    status: AcknowledgementStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuditCreate(BaseModel):
    department_id: UUID
    title: str = Field(min_length=1, max_length=255)
    auditor_id: UUID
    audit_date: date
    status: AuditStatus = AuditStatus.PLANNED


class AuditUpdate(BaseModel):
    department_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    auditor_id: UUID | None = None
    audit_date: date | None = None
    status: AuditStatus | None = None


class AuditResponse(BaseModel):
    id: UUID
    department_id: UUID
    department_name: str | None = None
    title: str
    auditor_id: UUID
    auditor_name: str | None = None
    audit_date: date
    status: AuditStatus
    issue_count: int = 0
    open_issue_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComplianceIssueCreate(BaseModel):
    audit_id: UUID | None = None
    owner_id: UUID
    severity: ComplianceSeverity
    description: str = Field(min_length=1)
    due_date: date
    status: ComplianceIssueStatus = ComplianceIssueStatus.OPEN


class ComplianceIssueUpdate(BaseModel):
    audit_id: UUID | None = None
    owner_id: UUID | None = None
    severity: ComplianceSeverity | None = None
    description: str | None = Field(default=None, min_length=1)
    due_date: date | None = None
    status: ComplianceIssueStatus | None = None


class ComplianceIssueResponse(BaseModel):
    id: UUID
    audit_id: UUID | None
    audit_title: str | None = None
    owner_id: UUID
    owner_name: str | None = None
    severity: ComplianceSeverity
    description: str
    due_date: date
    status: ComplianceIssueStatus
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeOption(BaseModel):
    id: UUID
    name: str
    email: str
    department_name: str | None = None


class GovernanceAnalyticsResponse(BaseModel):
    governance_score: Decimal
    compliance_rate: Decimal
    open_issues: int
    overdue_issues: int
    policy_completion: Decimal
    total_policies: int
    active_policies: int
    total_acknowledgements: int
    acknowledged_count: int
    pending_acknowledgements: int
    total_audits: int
    completed_audits: int
    closed_issues: int
    total_issues: int
