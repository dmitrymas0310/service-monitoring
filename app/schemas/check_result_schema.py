from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.common_schema import ApiSchema, CheckStatus, ErrorType


class CheckResultResponse(ApiSchema):
    id: UUID
    service_id: UUID = Field(alias="serviceId")
    endpoint_id: UUID = Field(alias="endpointId")
    checked_at: datetime = Field(alias="checkedAt")
    status: CheckStatus
    http_status_code: Optional[int] = Field(default=None, alias="httpStatusCode")
    latency_ms: Optional[int] = Field(default=None, alias="latencyMs")
    error_type: Optional[ErrorType] = Field(default=None, alias="errorType")
    error_message: Optional[str] = Field(default=None, alias="errorMessage")
    created_at: datetime = Field(alias="createdAt")


class CheckHistoryResponse(ApiSchema):
    items: list[CheckResultResponse]
    total: int
    limit: int
    offset: int
