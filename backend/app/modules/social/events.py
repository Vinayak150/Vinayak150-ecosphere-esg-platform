from app.core.events import event_bus

CSR_PARTICIPATION_APPROVED = "social.csr_participation.approved"
CSR_PARTICIPATION_REJECTED = "social.csr_participation.rejected"
CSR_ACTIVITY_COMPLETED = "social.csr_activity.completed"


def publish_csr_participation_approved(payload: dict[str, str | int]) -> None:
    event_bus.publish(CSR_PARTICIPATION_APPROVED, payload)


def publish_csr_participation_rejected(payload: dict[str, str | int]) -> None:
    event_bus.publish(CSR_PARTICIPATION_REJECTED, payload)


def publish_csr_activity_completed(payload: dict[str, str]) -> None:
    event_bus.publish(CSR_ACTIVITY_COMPLETED, payload)
