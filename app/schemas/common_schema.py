from enum import Enum

from pydantic import BaseModel, ConfigDict


class CheckStatus(str, Enum):
    UP = "UP"
    DOWN = "DOWN"


class ErrorType(str, Enum):
    HTTP_5XX = "HTTP_5XX"
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class HttpMethod(str, Enum):
    GET = "GET"


class StatsPeriod(str, Enum):
    month = "month"


class ApiSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ErrorResponse(ApiSchema):
    detail: str
