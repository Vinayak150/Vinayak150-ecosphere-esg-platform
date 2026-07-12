from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.social.models import ApprovalStatus, CSRActivityStatus
from app.shared.schemas.responses import PaginatedResponse, PaginationParams


class SocialListParams(PaginationParams):
    status: str | None = None
    department_id: UUID | None = None
    category: str | None = None
    approval_status: str | None = None
    csr_activity_id: UUID | None = None
    employee_id: UUID | None = None


class CsrActivityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    department_id: UUID
    description: str | None = None
    start_date: date
    end_date: date
    points: int = Field(default=0, ge=0)
    evidence_required: bool = False
    status: CSRActivityStatus = CSRActivityStatus.ACTIVE


class CsrActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    department_id: UUID | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    points: int | None = Field(default=None, ge=0)
    evidence_required: bool | None = None
    status: CSRActivityStatus | None = None


class CsrActivityResponse(BaseModel):
    id: UUID
    title: str
    category: str
    department_id: UUID
    department_name: str | None = None
    description: str | None
    start_date: date
    end_date: date
    points: int
    evidence_required: bool
    status: CSRActivityStatus
    participation_count: int = 0
    approved_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParticipationCreate(BaseModel):
    csr_activity_id: UUID
    proof_file: str | None = Field(default=None, max_length=500)


class ParticipationUpdate(BaseModel):
    proof_file: str | None = Field(default=None, max_length=500)


class ParticipationApprovalRequest(BaseModel):
    approval_status: ApprovalStatus = ApprovalStatus.APPROVED


class ParticipationRejectionRequest(BaseModel):
    rejection_reason: str | None = Field(default=None, max_length=500)


class ParticipationResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: str | None = None
    department_name: str | None = None
    csr_activity_id: UUID
    csr_activity_title: str | None = None
    proof_file: str | None
    approval_status: ApprovalStatus
    points_earned: int
    completion_date: date | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DepartmentParticipationItem(BaseModel):
    department_id: UUID
    department_name: str
    participation_count: int
    approved_count: int
    participation_rate: Decimal


class MonthlyCsrTrendPoint(BaseModel):
    month: str
    participation_count: int
    approved_count: int


class TopParticipatingDepartment(BaseModel):
    department_id: UUID
    department_name: str
    approved_participations: int
    total_points: int


class SocialAnalyticsResponse(BaseModel):
    participation_rate: Decimal
    total_employees: int
    total_participations: int
    approved_participations: int
    pending_approvals: int
    social_score: Decimal
    department_participation: list[DepartmentParticipationItem]
    monthly_csr_trend: list[MonthlyCsrTrendPoint]
    top_participating_departments: list[TopParticipatingDepartment]
    active_csr_activities: int
    completed_csr_activities: int


class EmployeeOption(BaseModel):
    id: UUID
    name: str
    email: str
    department_name: str | None


CsrActivityListResponse = PaginatedResponse[CsrActivityResponse]
ParticipationListResponse = PaginatedResponse[ParticipationResponse]
