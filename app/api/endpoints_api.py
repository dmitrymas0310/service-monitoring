from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.endpoint_schema import (
    EndpointCreateRequest,
    EndpointListResponse,
    EndpointResponse,
    EndpointUpdateRequest,
)
from app.services.monitoring_config_service import (
    get_endpoint,
    list_service_endpoints,
    patch_endpoint,
    register_endpoint,
)


router = APIRouter(tags=["Endpoint'ы"])


@router.post(
    "/api/v1/services/{serviceId}/endpoints",
    response_model=EndpointResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить endpoint к сервису",
    description=(
        "Регистрирует REST endpoint для указанного сервиса. В MVP поддерживается "
        "только HTTP method `GET`."
    ),
    response_description="Созданный endpoint.",
)
def create_endpoint_endpoint(
    request: EndpointCreateRequest,
    service_id: UUID = Path(alias="serviceId", description="Идентификатор сервиса."),
    db: Session = Depends(get_db),
) -> EndpointResponse:
    return register_endpoint(db, service_id, request)


@router.get(
    "/api/v1/services/{serviceId}/endpoints",
    response_model=EndpointListResponse,
    summary="Получить endpoint'ы сервиса",
    description="Возвращает список endpoint'ов, зарегистрированных для сервиса.",
    response_description="Список endpoint'ов сервиса.",
)
def list_service_endpoints_endpoint(
    service_id: UUID = Path(alias="serviceId", description="Идентификатор сервиса."),
    db: Session = Depends(get_db),
) -> EndpointListResponse:
    return list_service_endpoints(db, service_id)


@router.get(
    "/api/v1/endpoints/{endpointId}",
    response_model=EndpointResponse,
    summary="Получить endpoint по ID",
    description="Возвращает данные зарегистрированного endpoint'а.",
    response_description="Данные endpoint'а.",
)
def get_endpoint_endpoint(
    endpoint_id: UUID = Path(alias="endpointId", description="Идентификатор endpoint'а."),
    db: Session = Depends(get_db),
) -> EndpointResponse:
    return get_endpoint(db, endpoint_id)


@router.patch(
    "/api/v1/endpoints/{endpointId}",
    response_model=EndpointResponse,
    summary="Обновить endpoint",
    description="Частично обновляет параметры endpoint'а: URL, timeout, interval или активность.",
    response_description="Обновлённый endpoint.",
)
def patch_endpoint_endpoint(
    request: EndpointUpdateRequest,
    endpoint_id: UUID = Path(alias="endpointId", description="Идентификатор endpoint'а."),
    db: Session = Depends(get_db),
) -> EndpointResponse:
    return patch_endpoint(db, endpoint_id, request)
