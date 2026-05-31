from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Responsible, ServiceResponsible


def _to_dict(data: Any) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        return data.model_dump()
    return dict(data)


def create_responsible(db: Session, responsible_data: Any) -> Responsible:
    responsible = Responsible(**_to_dict(responsible_data))
    db.add(responsible)
    db.commit()
    db.refresh(responsible)
    return responsible


def link_responsible_to_service(
    db: Session,
    service_id: UUID,
    responsible_id: UUID,
) -> ServiceResponsible:
    existing_link = db.get(
        ServiceResponsible,
        {
            "service_id": service_id,
            "responsible_id": responsible_id,
        },
    )
    if existing_link is not None:
        return existing_link

    link = ServiceResponsible(
        service_id=service_id,
        responsible_id=responsible_id,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def get_responsibles_by_service_id(
    db: Session,
    service_id: UUID,
) -> list[Responsible]:
    query = (
        select(Responsible)
        .join(ServiceResponsible)
        .where(ServiceResponsible.service_id == service_id)
        .order_by(Responsible.full_name)
    )
    return list(db.execute(query).scalars().all())
