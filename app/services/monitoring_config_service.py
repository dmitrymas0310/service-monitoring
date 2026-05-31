from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.endpoint_repository import (
    create_endpoint,
    get_endpoint_by_id,
    get_endpoints_by_service_id,
    update_endpoint,
)
from app.repositories.responsible_repository import (
    create_responsible,
    get_responsibles_by_service_id,
    link_responsible_to_service,
)
from app.repositories.service_repository import (
    create_service,
    get_service_by_id,
    get_services,
)
from app.schemas.common_schema import HttpMethod
from app.schemas.endpoint_schema import (
    EndpointCreateRequest,
    EndpointListResponse,
    EndpointResponse,
    EndpointUpdateRequest,
)
from app.schemas.service_schema import (
    ServiceCreateRequest,
    ServiceListResponse,
    ServiceResponse,
)


def register_service(
    db: Session,
    request: ServiceCreateRequest,
) -> ServiceResponse:
    service = create_service(db, request)

    for responsible_data in request.responsibles:
        responsible = create_responsible(db, responsible_data)
        link_responsible_to_service(db, service.id, responsible.id)

    return build_service_response(db, service.id)


def list_services(db: Session) -> ServiceListResponse:
    services = get_services(db)
    return ServiceListResponse(
        items=[build_service_response(db, service.id) for service in services]
    )


def get_service(db: Session, service_id: UUID) -> ServiceResponse:
    return build_service_response(db, service_id)


def register_endpoint(
    db: Session,
    service_id: UUID,
    request: EndpointCreateRequest,
) -> EndpointResponse:
    ensure_service_exists(db, service_id)
    validate_endpoint_method(request.method)

    endpoint = create_endpoint(db, service_id, request)
    return EndpointResponse.model_validate(endpoint)


def list_service_endpoints(
    db: Session,
    service_id: UUID,
) -> EndpointListResponse:
    ensure_service_exists(db, service_id)
    endpoints = get_endpoints_by_service_id(db, service_id)
    return EndpointListResponse(
        items=[EndpointResponse.model_validate(endpoint) for endpoint in endpoints]
    )


def get_endpoint(db: Session, endpoint_id: UUID) -> EndpointResponse:
    endpoint = get_endpoint_by_id(db, endpoint_id)
    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found",
        )
    return EndpointResponse.model_validate(endpoint)


def patch_endpoint(
    db: Session,
    endpoint_id: UUID,
    request: EndpointUpdateRequest,
) -> EndpointResponse:
    if request.method is not None:
        validate_endpoint_method(request.method)

    endpoint = update_endpoint(db, endpoint_id, request)
    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found",
        )
    return EndpointResponse.model_validate(endpoint)


def build_service_response(db: Session, service_id: UUID) -> ServiceResponse:
    service = get_service_by_id(db, service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    responsibles = get_responsibles_by_service_id(db, service_id)
    return ServiceResponse.model_validate(
        {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "sla_target_percent": service.sla_target_percent,
            "is_active": service.is_active,
            "responsibles": responsibles,
            "created_at": service.created_at,
            "updated_at": service.updated_at,
        }
    )


def ensure_service_exists(db: Session, service_id: UUID) -> None:
    if get_service_by_id(db, service_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )


def validate_endpoint_method(method: HttpMethod) -> None:
    if method != HttpMethod.GET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only GET method is supported in MVP",
        )
