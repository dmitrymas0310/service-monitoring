from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Optional

import httpx

from app.models import Endpoint
from app.schemas.common_schema import CheckStatus, ErrorType
from app.utils import http_client


def check_endpoint(endpoint: Endpoint) -> dict[str, Any]:
    checked_at = datetime.now(timezone.utc)
    started_at = perf_counter()

    try:
        response = http_client.get(endpoint.url, endpoint.timeout_ms)
        latency_ms = _elapsed_ms(started_at)
        return _build_http_result(endpoint, checked_at, response, latency_ms)
    except httpx.TimeoutException as exc:
        return _build_error_result(
            endpoint=endpoint,
            checked_at=checked_at,
            started_at=started_at,
            error_type=ErrorType.TIMEOUT,
            error_message=str(exc) or "Request timed out",
        )
    except (httpx.ConnectError, httpx.NetworkError) as exc:
        return _build_error_result(
            endpoint=endpoint,
            checked_at=checked_at,
            started_at=started_at,
            error_type=ErrorType.CONNECTION_ERROR,
            error_message=str(exc) or "Connection error",
        )
    except httpx.HTTPError as exc:
        return _build_error_result(
            endpoint=endpoint,
            checked_at=checked_at,
            started_at=started_at,
            error_type=ErrorType.UNKNOWN_ERROR,
            error_message=str(exc) or "HTTP client error",
        )
    except Exception as exc:
        return _build_error_result(
            endpoint=endpoint,
            checked_at=checked_at,
            started_at=started_at,
            error_type=ErrorType.UNKNOWN_ERROR,
            error_message=str(exc) or "Unknown error",
        )


def _build_http_result(
    endpoint: Endpoint,
    checked_at: datetime,
    response: httpx.Response,
    latency_ms: int,
) -> dict[str, Any]:
    if response.status_code == 200:
        return _base_result(
            endpoint=endpoint,
            checked_at=checked_at,
            status=CheckStatus.UP,
            http_status_code=response.status_code,
            latency_ms=latency_ms,
        )

    if 500 <= response.status_code <= 599:
        return _base_result(
            endpoint=endpoint,
            checked_at=checked_at,
            status=CheckStatus.DOWN,
            http_status_code=response.status_code,
            latency_ms=latency_ms,
            error_type=ErrorType.HTTP_5XX,
            error_message=f"HTTP {response.status_code}",
        )

    return _base_result(
        endpoint=endpoint,
        checked_at=checked_at,
        status=CheckStatus.DOWN,
        http_status_code=response.status_code,
        latency_ms=latency_ms,
        error_type=ErrorType.UNKNOWN_ERROR,
        error_message=f"Unexpected HTTP status {response.status_code}",
    )


def _build_error_result(
    endpoint: Endpoint,
    checked_at: datetime,
    started_at: float,
    error_type: ErrorType,
    error_message: str,
) -> dict[str, Any]:
    return _base_result(
        endpoint=endpoint,
        checked_at=checked_at,
        status=CheckStatus.DOWN,
        latency_ms=_elapsed_ms(started_at),
        error_type=error_type,
        error_message=error_message,
    )


def _base_result(
    endpoint: Endpoint,
    checked_at: datetime,
    status: CheckStatus,
    http_status_code: Optional[int] = None,
    latency_ms: Optional[int] = None,
    error_type: Optional[ErrorType] = None,
    error_message: Optional[str] = None,
) -> dict[str, Any]:
    return {
        "service_id": endpoint.service_id,
        "endpoint_id": endpoint.id,
        "checked_at": checked_at,
        "status": status.value,
        "http_status_code": http_status_code,
        "latency_ms": latency_ms,
        "error_type": error_type.value if error_type is not None else None,
        "error_message": error_message,
    }


def _elapsed_ms(started_at: float) -> int:
    return round((perf_counter() - started_at) * 1000)
