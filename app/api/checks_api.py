from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.check_result_schema import CheckHistoryResponse
from app.schemas.common_schema import CheckStatus
from app.services.result_sla_service import (
    get_endpoint_check_history,
    get_service_check_history,
)


router = APIRouter(tags=["История проверок"])


@router.get(
    "/api/v1/services/{serviceId}/checks",
    response_model=CheckHistoryResponse,
    summary="Получить историю проверок сервиса",
    description=(
        "Возвращает сохранённые результаты проверок по сервису с фильтрацией "
        "по периоду, статусу и пагинацией."
    ),
    response_description="История проверок сервиса.",
)
def get_service_checks_endpoint(
    service_id: UUID = Path(alias="serviceId", description="Идентификатор сервиса."),
    date_from: Optional[datetime] = Query(
        default=None,
        alias="dateFrom",
        description="Начало периода фильтрации.",
    ),
    date_to: Optional[datetime] = Query(
        default=None,
        alias="dateTo",
        description="Конец периода фильтрации.",
    ),
    status: Optional[CheckStatus] = Query(
        default=None,
        description="Фильтр по статусу проверки: `UP` или `DOWN`.",
    ),
    limit: int = Query(default=100, ge=1, le=1000, description="Размер страницы."),
    offset: int = Query(default=0, ge=0, description="Смещение для пагинации."),
    db: Session = Depends(get_db),
) -> CheckHistoryResponse:
    return get_service_check_history(
        db=db,
        service_id=service_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/api/v1/endpoints/{endpointId}/checks",
    response_model=CheckHistoryResponse,
    summary="Получить историю проверок endpoint'а",
    description=(
        "Возвращает сохранённые результаты проверок по endpoint'у с фильтрацией "
        "по периоду, статусу и пагинацией."
    ),
    response_description="История проверок endpoint'а.",
)
def get_endpoint_checks_endpoint(
    endpoint_id: UUID = Path(alias="endpointId", description="Идентификатор endpoint'а."),
    date_from: Optional[datetime] = Query(
        default=None,
        alias="dateFrom",
        description="Начало периода фильтрации.",
    ),
    date_to: Optional[datetime] = Query(
        default=None,
        alias="dateTo",
        description="Конец периода фильтрации.",
    ),
    status: Optional[CheckStatus] = Query(
        default=None,
        description="Фильтр по статусу проверки: `UP` или `DOWN`.",
    ),
    limit: int = Query(default=100, ge=1, le=1000, description="Размер страницы."),
    offset: int = Query(default=0, ge=0, description="Смещение для пагинации."),
    db: Session = Depends(get_db),
) -> CheckHistoryResponse:
    return get_endpoint_check_history(
        db=db,
        endpoint_id=endpoint_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        limit=limit,
        offset=offset,
    )
