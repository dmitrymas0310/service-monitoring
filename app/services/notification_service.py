import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.check_result_repository import get_check_result_by_id
from app.repositories.endpoint_repository import get_endpoint_by_id
from app.repositories.notification_repository import create_notification_log
from app.repositories.responsible_repository import get_responsibles_by_service_id
from app.repositories.service_repository import get_service_by_id
from app.utils.email_sender import send_email


logger = logging.getLogger(__name__)


def send_failure_notification(
    db: Session,
    check_result_id: UUID,
    service_id: UUID,
    endpoint_id: UUID,
) -> None:
    service = get_service_by_id(db, service_id)
    endpoint = get_endpoint_by_id(db, endpoint_id)
    check_result = get_check_result_by_id(db, check_result_id)

    if service is None or endpoint is None or check_result is None:
        logger.error(
            "Cannot send notification: service=%s endpoint=%s check_result=%s",
            service_id,
            endpoint_id,
            check_result_id,
        )
        return

    responsibles = get_responsibles_by_service_id(db, service_id)
    subject = _build_subject(service.name, endpoint.name)
    body = _build_body(service, endpoint, check_result)

    for responsible in responsibles:
        status = "SENT"
        try:
            send_email(responsible.email, subject, body)
        except Exception:
            status = "FAILED"
            logger.exception(
                "Failed to send failure notification to %s",
                responsible.email,
            )

        create_notification_log(
            db,
            {
                "service_id": service_id,
                "endpoint_id": endpoint_id,
                "check_result_id": check_result_id,
                "responsible_id": responsible.id,
                "channel": "EMAIL",
                "status": status,
                "sent_at": datetime.now(timezone.utc),
            },
        )


def _build_subject(service_name: str, endpoint_name: str) -> str:
    return f"[Monitoring] DOWN: {service_name} / {endpoint_name}"


def _build_body(service, endpoint, check_result) -> str:
    lines = [
        "Endpoint availability check failed.",
        "",
        f"Service: {service.name}",
        f"Endpoint: {endpoint.name}",
        f"URL: {endpoint.url}",
        f"Checked at: {check_result.checked_at}",
        f"Status: {check_result.status}",
        f"HTTP status code: {check_result.http_status_code}",
        f"Latency ms: {check_result.latency_ms}",
        f"Error type: {check_result.error_type}",
        f"Error message: {check_result.error_message}",
    ]
    return "\n".join(lines)
