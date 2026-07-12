from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.auth.models import ActivityLog, Employee


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_recent_activity(self, limit: int = 15) -> list[tuple[ActivityLog, str | None]]:
        stmt = (
            select(ActivityLog, Employee.first_name, Employee.last_name)
            .outerjoin(Employee, ActivityLog.employee_id == Employee.id)
            .order_by(desc(ActivityLog.created_at))
            .limit(limit)
        )
        rows = self._db.execute(stmt).all()
        results: list[tuple[ActivityLog, str | None]] = []
        for log, first_name, last_name in rows:
            actor = None
            if first_name and last_name:
                actor = f"{first_name} {last_name}"
            results.append((log, actor))
        return results

    def get_activity_message(self, log: ActivityLog, actor: str | None) -> str:
        actor_label = actor or "System"
        entity_label = log.entity.replace("_", " ")
        return f"{actor_label} performed {log.action.lower()} on {entity_label}"
