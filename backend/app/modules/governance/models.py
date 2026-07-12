import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.models.base import BaseModel


class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class AcknowledgementStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"


class AuditStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ComplianceSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ComplianceIssueStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    OVERDUE = "OVERDUE"


class Policy(BaseModel):
    __tablename__ = "policies"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus, name="policy_status"),
        default=PolicyStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    acknowledgements: Mapped[list["PolicyAcknowledgement"]] = relationship(
        back_populates="policy"
    )


class PolicyAcknowledgement(BaseModel):
    __tablename__ = "policy_acknowledgements"
    __table_args__ = (
        UniqueConstraint("employee_id", "policy_id", name="uq_employee_policy_ack"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[AcknowledgementStatus] = mapped_column(
        Enum(AcknowledgementStatus, name="acknowledgement_status"),
        default=AcknowledgementStatus.PENDING,
        nullable=False,
        index=True,
    )

    policy: Mapped["Policy"] = relationship(back_populates="acknowledgements")


class Audit(BaseModel):
    __tablename__ = "audits"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    auditor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    audit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AuditStatus] = mapped_column(
        Enum(AuditStatus, name="audit_status"),
        default=AuditStatus.PLANNED,
        nullable=False,
        index=True,
    )

    compliance_issues: Mapped[list["ComplianceIssue"]] = relationship(
        back_populates="audit"
    )


class ComplianceIssue(BaseModel):
    __tablename__ = "compliance_issues"

    audit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    severity: Mapped[ComplianceSeverity] = mapped_column(
        Enum(ComplianceSeverity, name="compliance_severity"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[ComplianceIssueStatus] = mapped_column(
        Enum(ComplianceIssueStatus, name="compliance_issue_status"),
        default=ComplianceIssueStatus.OPEN,
        nullable=False,
        index=True,
    )

    audit: Mapped["Audit | None"] = relationship(back_populates="compliance_issues")
