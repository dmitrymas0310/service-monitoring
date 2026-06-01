from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import uuid

import httpx
import pytest

from app.services.health_check_service import check_endpoint


def _make_endpoint(url="http://example.com/health", timeout_ms=3000):
    ep = MagicMock()
    ep.id = uuid.uuid4()
    ep.service_id = uuid.uuid4()
    ep.url = url
    ep.timeout_ms = timeout_ms
    return ep


def _make_response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code=status_code)


def test_check_endpoint_200_returns_up():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", return_value=_make_response(200)):
        result = check_endpoint(endpoint)
    assert result["status"] == "UP"
    assert result["http_status_code"] == 200
    assert result["error_type"] is None
    assert result["error_message"] is None


def test_check_endpoint_200_has_latency():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", return_value=_make_response(200)):
        result = check_endpoint(endpoint)
    assert result["latency_ms"] is not None
    assert isinstance(result["latency_ms"], int)
    assert result["latency_ms"] >= 0


def test_check_endpoint_500_returns_down():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", return_value=_make_response(500)):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"
    assert result["error_type"] == "HTTP_5XX"
    assert "500" in result["error_message"]


def test_check_endpoint_503_returns_down():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", return_value=_make_response(503)):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"
    assert result["error_type"] == "HTTP_5XX"


def test_check_endpoint_404_returns_down():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", return_value=_make_response(404)):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"
    assert result["error_type"] == "UNKNOWN_ERROR"


def test_check_endpoint_301_returns_down():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", return_value=_make_response(301)):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"


def test_check_endpoint_timeout_returns_down():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", side_effect=httpx.TimeoutException("timed out")):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"
    assert result["error_type"] == "TIMEOUT"
    assert result["http_status_code"] is None


def test_check_endpoint_connect_error_returns_down():
    endpoint = _make_endpoint()
    with patch(
        "app.utils.http_client.get",
        side_effect=httpx.ConnectError("connection refused"),
    ):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"
    assert result["error_type"] == "CONNECTION_ERROR"


def test_check_endpoint_generic_http_error_returns_down():
    endpoint = _make_endpoint()
    with patch(
        "app.utils.http_client.get",
        side_effect=httpx.HTTPError("some http error"),
    ):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"
    assert result["error_type"] == "UNKNOWN_ERROR"


def test_check_endpoint_unexpected_exception_returns_down():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", side_effect=RuntimeError("boom")):
        result = check_endpoint(endpoint)
    assert result["status"] == "DOWN"
    assert result["error_type"] == "UNKNOWN_ERROR"


def test_check_endpoint_sets_service_and_endpoint_id():
    endpoint = _make_endpoint()
    with patch("app.utils.http_client.get", return_value=_make_response(200)):
        result = check_endpoint(endpoint)
    assert result["service_id"] == endpoint.service_id
    assert result["endpoint_id"] == endpoint.id


def test_check_endpoint_checked_at_is_recent():
    endpoint = _make_endpoint()
    before = datetime.now(timezone.utc)
    with patch("app.utils.http_client.get", return_value=_make_response(200)):
        result = check_endpoint(endpoint)
    after = datetime.now(timezone.utc)
    assert before <= result["checked_at"] <= after


def test_check_endpoint_error_message_set_on_timeout():
    endpoint = _make_endpoint()
    with patch(
        "app.utils.http_client.get",
        side_effect=httpx.TimeoutException("timed out"),
    ):
        result = check_endpoint(endpoint)
    assert result["error_message"] is not None
    assert len(result["error_message"]) > 0
