from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch
import uuid

import pytest

from app.services.result_sla_service import (
    _calculate_monthly_metrics,
    _is_down,
    _status_value,
    save_check_result,
)
from app.schemas.common_schema import CheckStatus


class TestIsDown:
    def test_down_status_enum_is_down(self):
        assert _is_down(CheckStatus.DOWN) is True

    def test_up_status_enum_is_not_down(self):
        assert _is_down(CheckStatus.UP) is False

    def test_down_string_is_down(self):
        assert _is_down("DOWN") is True

    def test_up_string_is_not_down(self):
        assert _is_down("UP") is False


class TestStatusValue:
    def test_none_returns_none(self):
        assert _status_value(None) is None

    def test_up_returns_string(self):
        assert _status_value(CheckStatus.UP) == "UP"

    def test_down_returns_string(self):
        assert _status_value(CheckStatus.DOWN) == "DOWN"


class TestCalculateMonthlyMetrics:
    def _make_result(self, status: str):
        r = MagicMock()
        r.status = status
        return r

    def test_no_results_returns_zeros(self):
        db = MagicMock()
        service_id = uuid.uuid4()
        with patch(
            "app.services.result_sla_service.get_monthly_check_results",
            return_value=[],
        ):
            metrics = _calculate_monthly_metrics(db, service_id, Decimal("99.9"))
        assert metrics["total_checks"] == 0
        assert metrics["up_checks"] == 0
        assert metrics["down_checks"] == 0
        assert metrics["uptime_percent"] == Decimal("0.00")
        assert metrics["sla_breached"] is False

    def test_all_up_100_percent(self):
        db = MagicMock()
        service_id = uuid.uuid4()
        results = [self._make_result("UP")] * 10
        with patch(
            "app.services.result_sla_service.get_monthly_check_results",
            return_value=results,
        ):
            metrics = _calculate_monthly_metrics(db, service_id, Decimal("99.9"))
        assert metrics["uptime_percent"] == Decimal("100.00")
        assert metrics["sla_breached"] is False

    def test_all_down_0_percent_and_sla_breached(self):
        db = MagicMock()
        service_id = uuid.uuid4()
        results = [self._make_result("DOWN")] * 5
        with patch(
            "app.services.result_sla_service.get_monthly_check_results",
            return_value=results,
        ):
            metrics = _calculate_monthly_metrics(db, service_id, Decimal("99.9"))
        assert metrics["uptime_percent"] == Decimal("0.00")
        assert metrics["sla_breached"] is True

    def test_mixed_uptime_calculation(self):
        db = MagicMock()
        service_id = uuid.uuid4()
        results = [self._make_result("UP")] * 3 + [self._make_result("DOWN")] * 1
        with patch(
            "app.services.result_sla_service.get_monthly_check_results",
            return_value=results,
        ):
            metrics = _calculate_monthly_metrics(db, service_id, Decimal("99.9"))
        assert metrics["total_checks"] == 4
        assert metrics["up_checks"] == 3
        assert metrics["down_checks"] == 1
        assert metrics["uptime_percent"] == Decimal("75.00")
        assert metrics["sla_breached"] is True

    def test_sla_not_breached_at_exact_target(self):
        db = MagicMock()
        service_id = uuid.uuid4()
        results = [self._make_result("UP")] * 999 + [self._make_result("DOWN")] * 1
        with patch(
            "app.services.result_sla_service.get_monthly_check_results",
            return_value=results,
        ):
            metrics = _calculate_monthly_metrics(db, service_id, Decimal("99.9"))
        assert metrics["uptime_percent"] == Decimal("99.90")
        assert metrics["sla_breached"] is False

    def test_uptime_rounded_to_two_decimals(self):
        db = MagicMock()
        service_id = uuid.uuid4()
        results = [self._make_result("UP")] * 2 + [self._make_result("DOWN")] * 1
        with patch(
            "app.services.result_sla_service.get_monthly_check_results",
            return_value=results,
        ):
            metrics = _calculate_monthly_metrics(db, service_id, Decimal("99.9"))
        assert metrics["uptime_percent"] == Decimal("66.67")


class TestSaveCheckResult:
    def _make_check_data(self, status="UP"):
        return {
            "service_id": uuid.uuid4(),
            "endpoint_id": uuid.uuid4(),
            "checked_at": datetime.now(timezone.utc),
            "status": status,
            "http_status_code": 200 if status == "UP" else 503,
            "latency_ms": 50,
            "error_type": None,
            "error_message": None,
        }

    def _make_mock_result(self, data, status="UP"):
        """Build a mock ORM result with both snake_case and camelCase attributes.

        Pydantic v2 with from_attributes=True reads alias names first, so
        MagicMock must expose the camelCase aliases explicitly.
        """
        from app.schemas.common_schema import CheckStatus, ErrorType

        now = datetime.now(timezone.utc)
        mock_result = MagicMock()
        mock_result.id = uuid.uuid4()
        mock_result.status = CheckStatus.UP if status == "UP" else CheckStatus.DOWN
        mock_result.service_id = data["service_id"]
        mock_result.serviceId = data["service_id"]
        mock_result.endpoint_id = data["endpoint_id"]
        mock_result.endpointId = data["endpoint_id"]
        mock_result.checked_at = data["checked_at"]
        mock_result.checkedAt = data["checked_at"]
        mock_result.http_status_code = 200 if status == "UP" else 503
        mock_result.httpStatusCode = mock_result.http_status_code
        mock_result.latency_ms = 50 if status == "UP" else None
        mock_result.latencyMs = mock_result.latency_ms
        mock_result.error_type = None if status == "UP" else ErrorType.HTTP_5XX
        mock_result.errorType = mock_result.error_type
        mock_result.error_message = None if status == "UP" else "HTTP 503"
        mock_result.errorMessage = mock_result.error_message
        mock_result.created_at = now
        mock_result.createdAt = now
        return mock_result

    def test_save_up_result_does_not_trigger_notification(self, db):
        notification_sender = MagicMock()
        data = self._make_check_data(status="UP")
        with patch(
            "app.services.result_sla_service.create_check_result"
        ) as mock_create:
            mock_create.return_value = self._make_mock_result(data, status="UP")
            save_check_result(db, data, notification_sender=notification_sender)

        notification_sender.assert_not_called()

    def test_save_down_result_triggers_notification(self, db):
        notification_sender = MagicMock()
        data = self._make_check_data(status="DOWN")
        with patch(
            "app.services.result_sla_service.create_check_result"
        ) as mock_create:
            mock_create.return_value = self._make_mock_result(data, status="DOWN")
            save_check_result(db, data, notification_sender=notification_sender)

        notification_sender.assert_called_once()
