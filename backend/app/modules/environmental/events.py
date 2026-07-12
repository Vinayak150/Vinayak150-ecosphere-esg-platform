from app.core.events import event_bus

CARBON_TRANSACTION_CREATED = "environmental.carbon_transaction.created"
GOAL_COMPLETED = "environmental.goal.completed"
GOAL_UPDATED = "environmental.goal.updated"


def publish_carbon_transaction_created(payload: dict[str, str | float]) -> None:
    event_bus.publish(CARBON_TRANSACTION_CREATED, payload)


def publish_goal_completed(payload: dict[str, str | float]) -> None:
    event_bus.publish(GOAL_COMPLETED, payload)


def publish_goal_updated(payload: dict[str, str | float]) -> None:
    event_bus.publish(GOAL_UPDATED, payload)
