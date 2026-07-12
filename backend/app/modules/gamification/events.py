from app.core.events import event_bus

CHALLENGE_COMPLETED = "gamification.challenge.completed"
BADGE_UNLOCKED = "gamification.badge.unlocked"
REWARD_REDEEMED = "gamification.reward.redeemed"
PARTICIPATION_APPROVED = "gamification.participation.approved"


def publish_challenge_completed(payload: dict[str, str | int]) -> None:
    event_bus.publish(CHALLENGE_COMPLETED, payload)


def publish_badge_unlocked(payload: dict[str, str]) -> None:
    event_bus.publish(BADGE_UNLOCKED, payload)


def publish_reward_redeemed(payload: dict[str, str | int]) -> None:
    event_bus.publish(REWARD_REDEEMED, payload)


def publish_participation_approved(payload: dict[str, str | int]) -> None:
    event_bus.publish(PARTICIPATION_APPROVED, payload)
