from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.models import ActivityLog


class ActivityLogService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def log_mutation(
        self,
        *,
        employee_id: UUID | None,
        action: str,
        entity: str,
        entity_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
        user_id: UUID | None = None,
    ) -> ActivityLog:
        log_entry = ActivityLog(
            employee_id=employee_id,
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            metadata_=metadata or {},
        )
        self._db.add(log_entry)
        self._db.flush()
        return log_entry
