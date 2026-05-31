from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.service_schema import (
    ServiceCreateRequest,
    ServiceListResponse,
    ServiceResponse,
)
from app.services.monitoring_config_service import (
    get_service,
    list_services,
    register_service,
)


router = APIRouter(prefix="/api/v1/services", tags=["Сервисы"])


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Зарегистрировать сервис",
    description=(
        "Создаёт мониторируемый сервис, сохраняет целевой SLA и список "
        "ответственных сотрудников."
    ),
    response_description="Созданный сервис с ответственными сотрудниками.",
)
def create_service_endpoint(
    request: ServiceCreateRequest,
    db: Session = Depends(get_db),
) -> ServiceResponse:
    return register_service(db, request)


@router.get(
    "",
    response_model=ServiceListResponse,
    summary="Получить список сервисов",
    description="Возвращает список зарегистрированных сервисов.",
    response_description="Список сервисов.",
)
def list_services_endpoint(db: Session = Depends(get_db)) -> ServiceListResponse:
    return list_services(db)


@router.get(
    "/{serviceId}",
    response_model=ServiceResponse,
    summary="Получить сервис по ID",
    description="Возвращает конфигурацию сервиса и список ответственных сотрудников.",
    response_description="Данные сервиса.",
)
def get_service_endpoint(
    service_id: UUID = Path(alias="serviceId", description="Идентификатор сервиса."),
    db: Session = Depends(get_db),
) -> ServiceResponse:
    return get_service(db, service_id)
