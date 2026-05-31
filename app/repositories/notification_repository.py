from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import NotificationLog


def _to_dict(data: Any) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    else:
        data = dict(data)
    return {
        key: value.value if isinstance(value, Enum) else value
        for key, value in data.items()
    }


def create_notification_log(db: Session, notification_data: Any) -> NotificationLog:
    notification_log = NotificationLog(**_to_dict(notification_data))
    db.add(notification_log)
    db.commit()
    db.refresh(notification_log)
    return notification_log


def get_notification_logs_by_service(
    db: Session,
    service_id: UUID,
) -> list[NotificationLog]:
    query = (
        select(NotificationLog)
        .where(NotificationLog.service_id == service_id)
        .order_by(NotificationLog.sent_at.desc())
    )
    return list(db.execute(query).scalars().all())
