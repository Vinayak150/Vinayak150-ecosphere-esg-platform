import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.models.base import BaseModel, EntityStatus


class GoalStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class TransactionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    CANCELLED = "CANCELLED"


class EmissionFactor(BaseModel):
    __tablename__ = "emission_factors"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    co2_factor: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EntityStatus] = mapped_column(
        Enum(EntityStatus, name="emission_factor_status"),
        default=EntityStatus.ACTIVE,
        nullable=False,
    )

    carbon_transactions: Mapped[list["CarbonTransaction"]] = relationship(
        back_populates="emission_factor"
    )


class CarbonTransaction(BaseModel):
    __tablename__ = "carbon_transactions"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    emission_factor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emission_factors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    calculated_emission: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="carbon_transaction_status"),
        default=TransactionStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    emission_factor: Mapped["EmissionFactor"] = relationship(back_populates="carbon_transactions")


class EnvironmentalGoal(BaseModel):
    __tablename__ = "environmental_goals"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    current_value: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=0, nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, name="goal_status"),
        default=GoalStatus.NOT_STARTED,
        nullable=False,
        index=True,
    )


class ProductEsgProfile(BaseModel):
    __tablename__ = "product_esg_profiles"

    product_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    carbon_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    recyclability: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    supplier_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EntityStatus] = mapped_column(
        Enum(EntityStatus, name="product_esg_status"),
        default=EntityStatus.ACTIVE,
        nullable=False,
    )
