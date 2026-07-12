from app.core.events import event_bus

COMPLIANCE_ISSUE_RAISED = "governance.compliance_issue.raised"
COMPLIANCE_ISSUE_CLOSED = "governance.compliance_issue.closed"
POLICY_ACKNOWLEDGED = "governance.policy.acknowledged"
AUDIT_COMPLETED = "governance.audit.completed"


def publish_compliance_issue_raised(payload: dict[str, str]) -> None:
    event_bus.publish(COMPLIANCE_ISSUE_RAISED, payload)


def publish_compliance_issue_closed(payload: dict[str, str]) -> None:
    event_bus.publish(COMPLIANCE_ISSUE_CLOSED, payload)


def publish_policy_acknowledged(payload: dict[str, str]) -> None:
    event_bus.publish(POLICY_ACKNOWLEDGED, payload)


def publish_audit_completed(payload: dict[str, str]) -> None:
    event_bus.publish(AUDIT_COMPLETED, payload)
