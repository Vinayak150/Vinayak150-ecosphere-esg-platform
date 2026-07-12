from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.environmental.models import GoalStatus, TransactionStatus
from app.shared.models.base import EntityStatus
from app.shared.schemas.responses import PaginatedResponse, PaginationParams


class EnvironmentalListParams(PaginationParams):
    status: str | None = None
    department_id: UUID | None = None
    source_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class EmissionFactorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source_type: str = Field(min_length=1, max_length=100)
    unit: str = Field(min_length=1, max_length=50)
    co2_factor: Decimal = Field(gt=0, decimal_places=4)
    description: str | None = None
    status: EntityStatus = EntityStatus.ACTIVE


class EmissionFactorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    source_type: str | None = Field(default=None, min_length=1, max_length=100)
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    co2_factor: Decimal | None = Field(default=None, gt=0, decimal_places=4)
    description: str | None = None
    status: EntityStatus | None = None


class EmissionFactorResponse(BaseModel):
    id: UUID
    name: str
    source_type: str
    unit: str
    co2_factor: Decimal
    description: str | None
    status: EntityStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CarbonTransactionCreate(BaseModel):
    department_id: UUID
    emission_factor_id: UUID
    activity_name: str = Field(min_length=1, max_length=255)
    quantity: Decimal = Field(gt=0, decimal_places=4)
    unit: str = Field(min_length=1, max_length=50)
    transaction_date: date
    status: TransactionStatus = TransactionStatus.ACTIVE


class CarbonTransactionUpdate(BaseModel):
    department_id: UUID | None = None
    emission_factor_id: UUID | None = None
    activity_name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: Decimal | None = Field(default=None, gt=0, decimal_places=4)
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    transaction_date: date | None = None
    status: TransactionStatus | None = None


class CarbonTransactionResponse(BaseModel):
    id: UUID
    department_id: UUID
    department_name: str | None = None
    emission_factor_id: UUID
    emission_factor_name: str | None = None
    activity_name: str
    quantity: Decimal
    unit: str
    calculated_emission: Decimal
    transaction_date: date
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CarbonCalculationRequest(BaseModel):
    emission_factor_id: UUID
    quantity: Decimal = Field(gt=0, decimal_places=4)


class CarbonCalculationResponse(BaseModel):
    emission_factor_id: UUID
    quantity: Decimal
    co2_factor: Decimal
    calculated_emission: Decimal
    unit: str


class EnvironmentalGoalCreate(BaseModel):
    department_id: UUID
    title: str = Field(min_length=1, max_length=255)
    target_value: Decimal = Field(gt=0, decimal_places=4)
    current_value: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=4)
    deadline: date
    status: GoalStatus = GoalStatus.NOT_STARTED


class EnvironmentalGoalUpdate(BaseModel):
    department_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    target_value: Decimal | None = Field(default=None, gt=0, decimal_places=4)
    current_value: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    deadline: date | None = None
    status: GoalStatus | None = None


class EnvironmentalGoalResponse(BaseModel):
    id: UUID
    department_id: UUID
    department_name: str | None = None
    title: str
    target_value: Decimal
    current_value: Decimal
    progress_percentage: Decimal
    deadline: date
    status: GoalStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductEsgCreate(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    carbon_score: Decimal = Field(ge=0, le=100, decimal_places=2)
    recyclability: Decimal = Field(ge=0, le=100, decimal_places=2)
    supplier_score: Decimal = Field(ge=0, le=100, decimal_places=2)
    notes: str | None = None
    status: EntityStatus = EntityStatus.ACTIVE


class ProductEsgUpdate(BaseModel):
    product_name: str | None = Field(default=None, min_length=1, max_length=255)
    carbon_score: Decimal | None = Field(default=None, ge=0, le=100, decimal_places=2)
    recyclability: Decimal | None = Field(default=None, ge=0, le=100, decimal_places=2)
    supplier_score: Decimal | None = Field(default=None, ge=0, le=100, decimal_places=2)
    notes: str | None = None
    status: EntityStatus | None = None


class ProductEsgResponse(BaseModel):
    id: UUID
    product_name: str
    carbon_score: Decimal
    recyclability: Decimal
    supplier_score: Decimal
    notes: str | None
    status: EntityStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DepartmentCarbonTotal(BaseModel):
    department_id: UUID
    department_name: str
    total_emission: Decimal


class MonthlyCarbonTrendPoint(BaseModel):
    month: str
    total_emission: Decimal


class TopCarbonSource(BaseModel):
    source_type: str
    emission_factor_name: str
    total_emission: Decimal


class GoalProgressItem(BaseModel):
    goal_id: UUID
    title: str
    department_name: str
    current_value: Decimal
    target_value: Decimal
    progress_percentage: Decimal
    status: GoalStatus
    deadline: date


class EnvironmentalAnalyticsResponse(BaseModel):
    department_carbon_totals: list[DepartmentCarbonTotal]
    monthly_carbon_trend: list[MonthlyCarbonTrendPoint]
    top_carbon_sources: list[TopCarbonSource]
    goal_progress: list[GoalProgressItem]
    total_emissions: Decimal
    active_goals: int
    completed_goals: int


EmissionFactorListResponse = PaginatedResponse[EmissionFactorResponse]
CarbonTransactionListResponse = PaginatedResponse[CarbonTransactionResponse]
EnvironmentalGoalListResponse = PaginatedResponse[EnvironmentalGoalResponse]
ProductEsgListResponse = PaginatedResponse[ProductEsgResponse]
