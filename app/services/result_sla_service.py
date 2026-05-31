from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import CheckResult
from app.repositories.check_result_repository import (
    count_check_results_by_endpoint,
    count_check_results_by_service,
    create_check_result,
    get_check_results_by_endpoint,
    get_check_results_by_service,
    get_last_check_result_by_service,
    get_monthly_check_results,
)
from app.repositories.service_repository import get_service_by_id, get_services
from app.schemas.check_result_schema import CheckHistoryResponse, CheckResultResponse
from app.schemas.common_schema import CheckStatus, StatsPeriod
from app.schemas.stats_schema import (
    ServiceStatsResponse,
    ServiceSummaryResponse,
    ServicesSummaryResponse,
)
from app.utils.datetime_utils import get_current_month_bounds


NotificationSender = Callable[[Session, CheckResult], None]


def save_check_result(
    db: Session,
    check_result_data: Any,
    notification_sender: Optional[NotificationSender] = None,
) -> CheckResultResponse:
    saved_result = create_check_result(db, check_result_data)

    if _is_down(saved_result.status):
        sender = notification_sender or _send_failure_notification
        sender(db, saved_result)

    return CheckResultResponse.model_validate(saved_result)


def get_service_check_history(
    db: Session,
    service_id: UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[CheckStatus] = None,
    limit: int = 100,
    offset: int = 0,
) -> CheckHistoryResponse:
    items = get_check_results_by_service(
        db=db,
        service_id=service_id,
        date_from=date_from,
        date_to=date_to,
        status=_status_value(status),
        limit=limit,
        offset=offset,
    )
    total = count_check_results_by_service(
        db=db,
        service_id=service_id,
        date_from=date_from,
        date_to=date_to,
        status=_status_value(status),
    )
    return _build_history_response(items, total, limit, offset)


def get_endpoint_check_history(
    db: Session,
    endpoint_id: UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[CheckStatus] = None,
    limit: int = 100,
    offset: int = 0,
) -> CheckHistoryResponse:
    items = get_check_results_by_endpoint(
        db=db,
        endpoint_id=endpoint_id,
        date_from=date_from,
        date_to=date_to,
        status=_status_value(status),
        limit=limit,
        offset=offset,
    )
    total = count_check_results_by_endpoint(
        db=db,
        endpoint_id=endpoint_id,
        date_from=date_from,
        date_to=date_to,
        status=_status_value(status),
    )
    return _build_history_response(items, total, limit, offset)


def get_service_stats(
    db: Session,
    service_id: UUID,
    period: StatsPeriod = StatsPeriod.month,
) -> ServiceStatsResponse:
    if period != StatsPeriod.month:
        raise ValueError("Only month period is supported")

    service = get_service_by_id(db, service_id)
    if service is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    metrics = _calculate_monthly_metrics(db, service.id, service.sla_target_percent)

    return ServiceStatsResponse(
        service_id=service.id,
        period=period,
        total_checks=metrics["total_checks"],
        up_checks=metrics["up_checks"],
        down_checks=metrics["down_checks"],
        uptime_percent=metrics["uptime_percent"],
        sla_target_percent=service.sla_target_percent,
        sla_breached=metrics["sla_breached"],
    )


def get_service_summary(db: Session, service_id: UUID) -> ServiceSummaryResponse:
    service = get_service_by_id(db, service_id)
    if service is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return _build_service_summary(db, service)


def get_services_summary(db: Session) -> ServicesSummaryResponse:
    services = get_services(db, is_active=True)
    return ServicesSummaryResponse(
        items=[_build_service_summary(db, service) for service in services]
    )


def _build_service_summary(db: Session, service) -> ServiceSummaryResponse:
    metrics = _calculate_monthly_metrics(db, service.id, service.sla_target_percent)
    last_check = get_last_check_result_by_service(db, service.id)

    current_status = None
    last_check_at = None
    last_error = None
    if last_check is not None:
        current_status = CheckStatus(last_check.status)
        last_check_at = last_check.checked_at
        last_error = last_check.error_message

    return ServiceSummaryResponse(
        service_id=service.id,
        service_name=service.name,
        current_status=current_status,
        sla_target_percent=service.sla_target_percent,
        uptime_percent=metrics["uptime_percent"],
        sla_breached=metrics["sla_breached"],
        total_checks=metrics["total_checks"],
        up_checks=metrics["up_checks"],
        down_checks=metrics["down_checks"],
        last_check_at=last_check_at,
        last_error=last_error,
    )


def _calculate_monthly_metrics(
    db: Session,
    service_id: UUID,
    sla_target_percent: Decimal,
) -> dict[str, Any]:
    month_start, month_end = get_current_month_bounds()
    results = get_monthly_check_results(db, service_id, month_start, month_end)

    total_checks = len(results)
    up_checks = sum(1 for result in results if result.status == CheckStatus.UP.value)
    down_checks = sum(1 for result in results if result.status == CheckStatus.DOWN.value)

    # Explicit MVP behavior: no monthly checks means no measured uptime yet,
    # so uptime is 0 and SLA is not considered breached.
    if total_checks == 0:
        uptime_percent = Decimal("0.00")
        sla_breached = False
    else:
        uptime_percent = (
            Decimal(up_checks) / Decimal(total_checks) * Decimal("100")
        ).quantize(Decimal("0.01"))
        sla_breached = uptime_percent < sla_target_percent

    return {
        "total_checks": total_checks,
        "up_checks": up_checks,
        "down_checks": down_checks,
        "uptime_percent": uptime_percent,
        "sla_breached": sla_breached,
    }


def _build_history_response(
    items: list[CheckResult],
    total: int,
    limit: int,
    offset: int,
) -> CheckHistoryResponse:
    return CheckHistoryResponse(
        items=[CheckResultResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


def _status_value(status: Optional[CheckStatus]) -> Optional[str]:
    if status is None:
        return None
    return status.value


def _is_down(status: Any) -> bool:
    if isinstance(status, CheckStatus):
        return status == CheckStatus.DOWN
    return status == CheckStatus.DOWN.value


def _notification_stub(db: Session, check_result: CheckResult) -> None:
    return None


def _send_failure_notification(db: Session, check_result: CheckResult) -> None:
    from app.services.notification_service import send_failure_notification

    send_failure_notification(
        db=db,
        check_result_id=check_result.id,
        service_id=check_result.service_id,
        endpoint_id=check_result.endpoint_id,
    )
