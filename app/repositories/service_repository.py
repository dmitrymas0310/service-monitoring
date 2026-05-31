from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Service


def _to_dict(data: Any, *, exclude_unset: bool = False) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=exclude_unset)
    return dict(data)


def _filter_service_fields(data: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = {
        "name",
        "description",
        "sla_target_percent",
        "is_active",
    }
    return {key: value for key, value in data.items() if key in allowed_fields}


def create_service(db: Session, service_data: Any) -> Service:
    service = Service(**_filter_service_fields(_to_dict(service_data)))
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def get_service_by_id(db: Session, service_id: UUID) -> Optional[Service]:
    return db.get(Service, service_id)


def get_services(db: Session, is_active: Optional[bool] = None) -> list[Service]:
    query = select(Service)
    if is_active is not None:
        query = query.where(Service.is_active == is_active)
    return list(db.execute(query.order_by(Service.created_at.desc())).scalars().all())


def update_service(
    db: Session,
    service_id: UUID,
    update_data: Any,
) -> Optional[Service]:
    service = get_service_by_id(db, service_id)
    if service is None:
        return None

    for field, value in _filter_service_fields(
        _to_dict(update_data, exclude_unset=True)
    ).items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service
