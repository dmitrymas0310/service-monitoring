import uuid
from datetime import datetime, timezone


def test_services_summary_empty(client):
    resp = client.get("/api/v1/services/summary")
    assert resp.status_code == 200
    assert resp.json()["items"] == []


def test_services_summary_contains_active_service(client, created_service):
    resp = client.get("/api/v1/services/summary")
    data = resp.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["serviceId"] == created_service["id"]
    assert item["serviceName"] == created_service["name"]


def test_services_summary_fields(client, created_service):
    resp = client.get("/api/v1/services/summary")
    item = resp.json()["items"][0]
    assert "serviceId" in item
    assert "serviceName" in item
    assert "slaTargetPercent" in item
    assert "uptimePercent" in item
    assert "slaBreached" in item
    assert "totalChecks" in item
    assert "upChecks" in item
    assert "downChecks" in item


def test_services_summary_no_checks_zero_uptime(client, created_service):
    resp = client.get("/api/v1/services/summary")
    item = resp.json()["items"][0]
    assert item["totalChecks"] == 0
    assert float(item["uptimePercent"]) == 0.0
    assert item["slaBreached"] is False
    assert item["currentStatus"] is None


def test_services_summary_with_checks(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="DOWN")

    resp = client.get("/api/v1/services/summary")
    item = resp.json()["items"][0]
    assert item["totalChecks"] == 3
    assert item["upChecks"] == 2
    assert item["downChecks"] == 1


def test_service_summary_by_id(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["serviceId"] == service_id
    assert data["serviceName"] == created_service["name"]


def test_service_summary_not_found(client):
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/services/{fake_id}/summary")
    assert resp.status_code == 404


def test_service_summary_current_status_up(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="DOWN")
    insert_check_result(db, service_id, endpoint_id, status="UP")

    resp = client.get(f"/api/v1/services/{service_id}/summary")
    data = resp.json()
    assert data["currentStatus"] == "UP"


def test_service_summary_sla_breached(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    for _ in range(9):
        insert_check_result(db, service_id, endpoint_id, status="DOWN")
    insert_check_result(db, service_id, endpoint_id, status="UP")

    resp = client.get(f"/api/v1/services/{service_id}/summary")
    data = resp.json()
    assert data["slaBreached"] is True


def test_service_summary_sla_not_breached_perfect_uptime(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    for _ in range(10):
        insert_check_result(db, service_id, endpoint_id, status="UP")

    resp = client.get(f"/api/v1/services/{service_id}/summary")
    data = resp.json()
    assert data["slaBreached"] is False
    assert float(data["uptimePercent"]) == 100.0


def test_service_stats_default_month_period(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["period"] == "month"
    assert data["serviceId"] == service_id


def test_service_stats_fields(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/stats")
    data = resp.json()
    assert "totalChecks" in data
    assert "upChecks" in data
    assert "downChecks" in data
    assert "uptimePercent" in data
    assert "slaTargetPercent" in data
    assert "slaBreached" in data


def test_service_stats_uptime_calculation(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    for _ in range(3):
        insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="DOWN")

    resp = client.get(f"/api/v1/services/{service_id}/stats")
    data = resp.json()
    assert data["totalChecks"] == 4
    assert data["upChecks"] == 3
    assert data["downChecks"] == 1
    assert float(data["uptimePercent"]) == 75.0


def test_service_stats_not_found(client):
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/services/{fake_id}/stats")
    assert resp.status_code == 404


def test_service_stats_no_checks_zero(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/stats")
    data = resp.json()
    assert data["totalChecks"] == 0
    assert float(data["uptimePercent"]) == 0.0
    assert data["slaBreached"] is False
