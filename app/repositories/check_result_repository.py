from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CheckResult


def _to_dict(data: Any) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    else:
        data = dict(data)
    return {key: _value(value) for key, value in data.items()}


def _filter_check_result_fields(data: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = {
        "service_id",
        "endpoint_id",
        "checked_at",
        "status",
        "http_status_code",
        "latency_ms",
        "error_type",
        "error_message",
    }
    return {key: value for key, value in data.items() if key in allowed_fields}


def _value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def create_check_result(db: Session, check_result_data: Any) -> CheckResult:
    check_result = CheckResult(**_filter_check_result_fields(_to_dict(check_result_data)))
    db.add(check_result)
    db.commit()
    db.refresh(check_result)
    return check_result


def get_check_result_by_id(
    db: Session,
    check_result_id: UUID,
) -> Optional[CheckResult]:
    return db.get(CheckResult, check_result_id)


def get_check_results_by_service(
    db: Session,
    service_id: UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[CheckResult]:
    query = _service_results_query(service_id, date_from, date_to, status)
    query = query.order_by(CheckResult.checked_at.desc()).limit(limit).offset(offset)
    return list(db.execute(query).scalars().all())


def get_check_results_by_endpoint(
    db: Session,
    endpoint_id: UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[CheckResult]:
    query = select(CheckResult).where(CheckResult.endpoint_id == endpoint_id)
    query = _apply_date_and_status_filters(query, date_from, date_to, status)
    query = query.order_by(CheckResult.checked_at.desc()).limit(limit).offset(offset)
    return list(db.execute(query).scalars().all())


def get_last_check_result_by_service(
    db: Session,
    service_id: UUID,
) -> Optional[CheckResult]:
    query = (
        select(CheckResult)
        .where(CheckResult.service_id == service_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(1)
    )
    return db.execute(query).scalars().first()


def get_monthly_check_results(
    db: Session,
    service_id: UUID,
    month_start: datetime,
    month_end: datetime,
) -> list[CheckResult]:
    query = (
        select(CheckResult)
        .where(CheckResult.service_id == service_id)
        .where(CheckResult.checked_at >= month_start)
        .where(CheckResult.checked_at < month_end)
        .order_by(CheckResult.checked_at.asc())
    )
    return list(db.execute(query).scalars().all())


def count_check_results_by_service(
    db: Session,
    service_id: UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = None,
) -> int:
    query = select(func.count(CheckResult.id)).where(CheckResult.service_id == service_id)
    query = _apply_date_and_status_filters(query, date_from, date_to, status)
    return int(db.execute(query).scalar_one())


def count_check_results_by_endpoint(
    db: Session,
    endpoint_id: UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = None,
) -> int:
    query = select(func.count(CheckResult.id)).where(
        CheckResult.endpoint_id == endpoint_id
    )
    query = _apply_date_and_status_filters(query, date_from, date_to, status)
    return int(db.execute(query).scalar_one())


def _service_results_query(
    service_id: UUID,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    status: Optional[str],
):
    query = select(CheckResult).where(CheckResult.service_id == service_id)
    return _apply_date_and_status_filters(query, date_from, date_to, status)


def _apply_date_and_status_filters(
    query,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    status: Optional[str],
):
    if date_from is not None:
        query = query.where(CheckResult.checked_at >= date_from)
    if date_to is not None:
        query = query.where(CheckResult.checked_at <= date_to)
    if status is not None:
        query = query.where(CheckResult.status == _value(status))
    return query
