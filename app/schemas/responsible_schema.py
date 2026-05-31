from __future__ import annotations

from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common_schema import ApiSchema


class ResponsibleCreate(ApiSchema):
    full_name: str = Field(alias="fullName")
    email: EmailStr


class ResponsibleResponse(ApiSchema):
    id: UUID
    full_name: str = Field(alias="fullName")
    email: EmailStr
