from datetime import date

from app.modules.gamification.models import Challenge, ChallengeStatus, ParticipationApproval
from app.modules.gamification.schemas import (
    ChallengeCreate,
    ParticipationSubmit,
)
from app.shared.exceptions.base import BusinessRuleViolationError, ValidationError


def validate_challenge_deadline(deadline: date) -> None:
    if deadline < date.today():
        raise ValidationError("Challenge deadline cannot be in the past")


def validate_positive_xp(xp: int) -> None:
    if xp < 0:
        raise ValidationError("XP must be zero or greater")


def validate_active_challenge(challenge: Challenge) -> None:
    if challenge.status != ChallengeStatus.ACTIVE:
        raise BusinessRuleViolationError("You can only join active challenges")
    if challenge.deadline < date.today():
        raise BusinessRuleViolationError("Challenge deadline has passed")


def validate_submission_proof(
    challenge: Challenge, payload: ParticipationSubmit
) -> None:
    if challenge.evidence_required and not payload.proof_file:
        raise ValidationError("Proof is required for this challenge")


def validate_approval_proof(challenge: Challenge, proof_file: str | None) -> None:
    if challenge.evidence_required and not proof_file:
        raise ValidationError("Approval requires proof when evidence is required")


def validate_participation_for_review(approval_status: ParticipationApproval) -> None:
    if approval_status not in (
        ParticipationApproval.SUBMITTED,
        ParticipationApproval.PENDING,
    ):
        raise BusinessRuleViolationError("Participation is not eligible for review")


ALLOWED_UNLOCK_RULES = frozenset({"total_xp", "approved_challenges"})


def validate_unlock_rule(unlock_rule: dict) -> None:
    if not unlock_rule:
        return
    rule_type = unlock_rule.get("rule")
    threshold = unlock_rule.get("threshold")
    if rule_type is None and threshold is None:
        return
    if rule_type not in ALLOWED_UNLOCK_RULES:
        raise ValidationError(
            f"Invalid unlock rule type: {rule_type}. "
            f"Allowed values: {', '.join(sorted(ALLOWED_UNLOCK_RULES))}"
        )
    if threshold is None or not isinstance(threshold, int) or threshold < 0:
        raise ValidationError("Unlock rule threshold must be a non-negative integer")


def validate_challenge_create(payload: ChallengeCreate) -> None:
    validate_challenge_deadline(payload.deadline)
    validate_positive_xp(payload.xp)


def validate_reward_redemption(available_xp: int, points_required: int, stock: int) -> None:
    if stock <= 0:
        raise BusinessRuleViolationError("Reward is out of stock")
    if available_xp < points_required:
        raise BusinessRuleViolationError("Insufficient XP to redeem this reward")
