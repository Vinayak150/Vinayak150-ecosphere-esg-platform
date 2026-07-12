import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.models.base import BaseModel


class ChallengeStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ChallengeDifficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    EXPERT = "EXPERT"


class ParticipationApproval(str, enum.Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class BadgeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class RewardStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    ARCHIVED = "ARCHIVED"


class Challenge(BaseModel):
    __tablename__ = "challenges"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    difficulty: Mapped[ChallengeDifficulty] = mapped_column(
        Enum(ChallengeDifficulty, name="challenge_difficulty"),
        default=ChallengeDifficulty.MEDIUM,
        nullable=False,
        index=True,
    )
    evidence_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[ChallengeStatus] = mapped_column(
        Enum(ChallengeStatus, name="challenge_status"),
        default=ChallengeStatus.DRAFT,
        nullable=False,
        index=True,
    )

    participations: Mapped[list["ChallengeParticipation"]] = relationship(
        back_populates="challenge"
    )


class ChallengeParticipation(BaseModel):
    __tablename__ = "challenge_participation"
    __table_args__ = (
        UniqueConstraint("employee_id", "challenge_id", name="uq_employee_challenge"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("challenges.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    proof_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approval_status: Mapped[ParticipationApproval] = mapped_column(
        Enum(ParticipationApproval, name="challenge_participation_approval_status"),
        default=ParticipationApproval.PENDING,
        nullable=False,
        index=True,
    )
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="participations")


class Badge(BaseModel):
    __tablename__ = "badges"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unlock_rule: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[BadgeStatus] = mapped_column(
        Enum(BadgeStatus, name="badge_status"),
        default=BadgeStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    employee_badges: Mapped[list["EmployeeBadge"]] = relationship(back_populates="badge")


class EmployeeBadge(BaseModel):
    __tablename__ = "employee_badges"
    __table_args__ = (
        UniqueConstraint("employee_id", "badge_id", name="uq_employee_badge"),
    )

    badge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("badges.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    badge: Mapped["Badge"] = relationship(back_populates="employee_badges")


class Reward(BaseModel):
    __tablename__ = "rewards"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    points_required: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[RewardStatus] = mapped_column(
        Enum(RewardStatus, name="reward_status"),
        default=RewardStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    redemptions: Mapped[list["RewardRedemption"]] = relationship(back_populates="reward")


class RewardRedemption(BaseModel):
    __tablename__ = "reward_redemptions"

    reward_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rewards.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    redeemed_points: Mapped[int] = mapped_column(Integer, nullable=False)
    redeemed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    reward: Mapped["Reward"] = relationship(back_populates="redemptions")
