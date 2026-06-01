import uuid
from datetime import datetime, timedelta, timezone


def test_service_checks_empty(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/checks")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 100
    assert data["offset"] == 0


def test_service_checks_returns_inserted_results(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="DOWN")

    resp = client.get(f"/api/v1/services/{service_id}/checks")
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_service_checks_filter_by_status_up(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="DOWN")

    resp = client.get(f"/api/v1/services/{service_id}/checks?status=UP")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "UP"


def test_service_checks_filter_by_status_down(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="DOWN")

    resp = client.get(f"/api/v1/services/{service_id}/checks?status=DOWN")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "DOWN"


def test_service_checks_pagination(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    for _ in range(5):
        insert_check_result(db, service_id, endpoint_id, status="UP")

    resp = client.get(f"/api/v1/services/{service_id}/checks?limit=2&offset=0")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_service_checks_pagination_offset(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    for _ in range(5):
        insert_check_result(db, service_id, endpoint_id, status="UP")

    resp = client.get(f"/api/v1/services/{service_id}/checks?limit=2&offset=4")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 1


def test_service_checks_date_filter(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(days=10)
    insert_check_result(db, service_id, endpoint_id, status="UP", checked_at=old_time)
    insert_check_result(db, service_id, endpoint_id, status="UP", checked_at=now)

    date_from = (now - timedelta(days=1)).isoformat()
    resp = client.get(
        f"/api/v1/services/{service_id}/checks",
        params={"dateFrom": date_from},
    )
    data = resp.json()
    assert data["total"] == 1


def test_service_checks_result_fields(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="UP")

    resp = client.get(f"/api/v1/services/{service_id}/checks")
    item = resp.json()["items"][0]
    assert "id" in item
    assert "serviceId" in item
    assert "endpointId" in item
    assert "checkedAt" in item
    assert "status" in item
    assert "createdAt" in item


def test_endpoint_checks_empty(client, created_endpoint):
    endpoint_id = created_endpoint["id"]
    resp = client.get(f"/api/v1/endpoints/{endpoint_id}/checks")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_endpoint_checks_returns_results(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="DOWN")

    resp = client.get(f"/api/v1/endpoints/{endpoint_id}/checks")
    data = resp.json()
    assert data["total"] == 2


def test_endpoint_checks_filter_status(client, db, created_endpoint):
    from tests.conftest import insert_check_result

    service_id = created_endpoint["serviceId"]
    endpoint_id = created_endpoint["id"]
    insert_check_result(db, service_id, endpoint_id, status="UP")
    insert_check_result(db, service_id, endpoint_id, status="DOWN")

    resp = client.get(f"/api/v1/endpoints/{endpoint_id}/checks?status=DOWN")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "DOWN"


def test_endpoint_checks_invalid_status(client, created_endpoint):
    endpoint_id = created_endpoint["id"]
    resp = client.get(f"/api/v1/endpoints/{endpoint_id}/checks?status=INVALID")
    assert resp.status_code == 422


def test_service_checks_invalid_limit(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/checks?limit=0")
    assert resp.status_code == 422


def test_service_checks_limit_above_max(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/checks?limit=9999")
    assert resp.status_code == 422
