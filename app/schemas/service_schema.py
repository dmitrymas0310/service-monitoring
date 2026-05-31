from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.common_schema import ApiSchema
from app.schemas.responsible_schema import ResponsibleCreate, ResponsibleResponse


class ServiceCreateRequest(ApiSchema):
    name: str
    description: Optional[str] = None
    sla_target_percent: Decimal = Field(default=Decimal("99.9"), alias="slaTargetPercent")
    responsibles: list[ResponsibleCreate] = Field(default_factory=list)


class ServiceUpdateRequest(ApiSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    sla_target_percent: Optional[Decimal] = Field(default=None, alias="slaTargetPercent")
    is_active: Optional[bool] = Field(default=None, alias="isActive")


class ServiceResponse(ApiSchema):
    id: UUID
    name: str
    description: Optional[str] = None
    sla_target_percent: Decimal = Field(alias="slaTargetPercent")
    is_active: bool = Field(alias="isActive")
    responsibles: list[ResponsibleResponse] = Field(default_factory=list)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ServiceListResponse(ApiSchema):
    items: list[ServiceResponse]
