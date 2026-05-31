from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common_schema import StatsPeriod
from app.schemas.stats_schema import (
    ServiceStatsResponse,
    ServiceSummaryResponse,
    ServicesSummaryResponse,
)
from app.services.result_sla_service import (
    get_service_stats,
    get_service_summary,
    get_services_summary,
)


router = APIRouter(tags=["Статистика и SLA"])


@router.get(
    "/api/v1/services/summary",
    response_model=ServicesSummaryResponse,
    summary="Получить сводку по активным сервисам",
    description="Возвращает текущий статус, uptime, SLA и последнюю ошибку для всех активных сервисов.",
    response_description="Сводка по активным сервисам.",
)
def get_services_summary_endpoint(
    db: Session = Depends(get_db),
) -> ServicesSummaryResponse:
    return get_services_summary(db)


@router.get(
    "/api/v1/services/{serviceId}/summary",
    response_model=ServiceSummaryResponse,
    summary="Получить сводку по сервису",
    description="Возвращает текущий статус, uptime, SLA, счётчики проверок и последнюю ошибку сервиса.",
    response_description="Сводка по сервису.",
)
def get_service_summary_endpoint(
    service_id: UUID = Path(alias="serviceId", description="Идентификатор сервиса."),
    db: Session = Depends(get_db),
) -> ServiceSummaryResponse:
    return get_service_summary(db, service_id)


@router.get(
    "/api/v1/services/{serviceId}/stats",
    response_model=ServiceStatsResponse,
    summary="Получить uptime и SLA сервиса",
    description=(
        "Рассчитывает uptime и признак нарушения SLA за выбранный период. "
        "В MVP поддерживается только `period=month`."
    ),
    response_description="Статистика uptime и SLA.",
)
def get_service_stats_endpoint(
    service_id: UUID = Path(alias="serviceId", description="Идентификатор сервиса."),
    period: StatsPeriod = Query(
        default=StatsPeriod.month,
        description="Период расчёта. В MVP поддерживается только `month`.",
    ),
    db: Session = Depends(get_db),
) -> ServiceStatsResponse:
    return get_service_stats(db, service_id, period)
