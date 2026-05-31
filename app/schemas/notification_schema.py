from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common_schema import ApiSchema


class NotificationLogResponse(ApiSchema):
    id: UUID
    service_id: UUID = Field(alias="serviceId")
    endpoint_id: UUID = Field(alias="endpointId")
    check_result_id: UUID = Field(alias="checkResultId")
    responsible_id: UUID = Field(alias="responsibleId")
    channel: str
    status: str
    sent_at: datetime = Field(alias="sentAt")


class NotificationLogListResponse(ApiSchema):
    items: list[NotificationLogResponse]
