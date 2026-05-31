from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.common_schema import ApiSchema, HttpMethod


class EndpointCreateRequest(ApiSchema):
    name: str
    url: str
    method: HttpMethod = HttpMethod.GET
    timeout_ms: int = Field(default=2000, alias="timeoutMs")
    check_interval_sec: int = Field(default=10, alias="checkIntervalSec")
    is_active: bool = Field(default=True, alias="isActive")


class EndpointUpdateRequest(ApiSchema):
    name: Optional[str] = None
    url: Optional[str] = None
    method: Optional[HttpMethod] = None
    timeout_ms: Optional[int] = Field(default=None, alias="timeoutMs")
    check_interval_sec: Optional[int] = Field(default=None, alias="checkIntervalSec")
    is_active: Optional[bool] = Field(default=None, alias="isActive")


class EndpointResponse(ApiSchema):
    id: UUID
    service_id: UUID = Field(alias="serviceId")
    name: str
    url: str
    method: HttpMethod
    timeout_ms: int = Field(alias="timeoutMs")
    check_interval_sec: int = Field(alias="checkIntervalSec")
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class EndpointListResponse(ApiSchema):
    items: list[EndpointResponse]
