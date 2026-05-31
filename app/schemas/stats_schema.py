from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.common_schema import ApiSchema, CheckStatus, StatsPeriod


class ServiceStatsResponse(ApiSchema):
    service_id: UUID = Field(alias="serviceId")
    period: StatsPeriod = StatsPeriod.month
    total_checks: int = Field(alias="totalChecks")
    up_checks: int = Field(alias="upChecks")
    down_checks: int = Field(alias="downChecks")
    uptime_percent: Decimal = Field(alias="uptimePercent")
    sla_target_percent: Decimal = Field(alias="slaTargetPercent")
    sla_breached: bool = Field(alias="slaBreached")


class ServiceSummaryResponse(ApiSchema):
    service_id: UUID = Field(alias="serviceId")
    service_name: str = Field(alias="serviceName")
    current_status: Optional[CheckStatus] = Field(default=None, alias="currentStatus")
    sla_target_percent: Decimal = Field(alias="slaTargetPercent")
    uptime_percent: Decimal = Field(alias="uptimePercent")
    sla_breached: bool = Field(alias="slaBreached")
    total_checks: int = Field(alias="totalChecks")
    up_checks: int = Field(alias="upChecks")
    down_checks: int = Field(alias="downChecks")
    last_check_at: Optional[datetime] = Field(default=None, alias="lastCheckAt")
    last_error: Optional[str] = Field(default=None, alias="lastError")


class ServicesSummaryResponse(ApiSchema):
    items: list[ServiceSummaryResponse]
