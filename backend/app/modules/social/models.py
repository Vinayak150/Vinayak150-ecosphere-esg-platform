import enum
import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.models.base import BaseModel


class CSRActivityStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CsrActivity(BaseModel):
    __tablename__ = "csr_activities"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evidence_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[CSRActivityStatus] = mapped_column(
        Enum(CSRActivityStatus, name="csr_activity_status"),
        default=CSRActivityStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    participations: Mapped[list["EmployeeParticipation"]] = relationship(
        back_populates="csr_activity"
    )


class EmployeeParticipation(BaseModel):
    __tablename__ = "employee_participation"
    __table_args__ = (
        UniqueConstraint("employee_id", "csr_activity_id", name="uq_employee_csr_activity"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    csr_activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("csr_activities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    proof_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="participation_approval_status"),
        default=ApprovalStatus.PENDING,
        nullable=False,
        index=True,
    )
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    csr_activity: Mapped["CsrActivity"] = relationship(back_populates="participations")
