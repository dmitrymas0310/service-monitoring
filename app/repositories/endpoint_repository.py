from enum import Enum
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Endpoint


def _to_dict(data: Any, *, exclude_unset: bool = False) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump(exclude_unset=exclude_unset)
    else:
        data = dict(data)
    return {
        key: value.value if isinstance(value, Enum) else value
        for key, value in data.items()
    }


def _filter_endpoint_fields(data: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = {
        "name",
        "url",
        "method",
        "timeout_ms",
        "check_interval_sec",
        "is_active",
    }
    return {key: value for key, value in data.items() if key in allowed_fields}


def create_endpoint(db: Session, service_id: UUID, endpoint_data: Any) -> Endpoint:
    endpoint = Endpoint(
        service_id=service_id,
        **_filter_endpoint_fields(_to_dict(endpoint_data)),
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint


def get_endpoint_by_id(db: Session, endpoint_id: UUID) -> Optional[Endpoint]:
    return db.get(Endpoint, endpoint_id)


def get_endpoints_by_service_id(
    db: Session,
    service_id: UUID,
    is_active: Optional[bool] = None,
) -> list[Endpoint]:
    query = select(Endpoint).where(Endpoint.service_id == service_id)
    if is_active is not None:
        query = query.where(Endpoint.is_active == is_active)
    return list(db.execute(query.order_by(Endpoint.created_at.desc())).scalars().all())


def get_active_endpoints(db: Session) -> list[Endpoint]:
    query = select(Endpoint).where(Endpoint.is_active.is_(True))
    return list(db.execute(query.order_by(Endpoint.created_at.desc())).scalars().all())


def update_endpoint(
    db: Session,
    endpoint_id: UUID,
    update_data: Any,
) -> Optional[Endpoint]:
    endpoint = get_endpoint_by_id(db, endpoint_id)
    if endpoint is None:
        return None

    for field, value in _filter_endpoint_fields(
        _to_dict(update_data, exclude_unset=True)
    ).items():
        setattr(endpoint, field, value)

    db.commit()
    db.refresh(endpoint)
    return endpoint
