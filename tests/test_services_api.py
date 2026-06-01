import uuid


def test_create_service_returns_201(client, service_payload):
    resp = client.post("/api/v1/services", json=service_payload)
    assert resp.status_code == 201


def test_create_service_response_fields(client, service_payload):
    resp = client.post("/api/v1/services", json=service_payload)
    data = resp.json()
    assert "id" in data
    assert data["name"] == service_payload["name"]
    assert data["description"] == service_payload["description"]
    assert float(data["slaTargetPercent"]) == float(service_payload["slaTargetPercent"])
    assert data["isActive"] is True
    assert "createdAt" in data
    assert "updatedAt" in data


def test_create_service_with_responsibles(client, service_payload):
    resp = client.post("/api/v1/services", json=service_payload)
    data = resp.json()
    assert len(data["responsibles"]) == 1
    assert data["responsibles"][0]["fullName"] == "Alice Smith"
    assert data["responsibles"][0]["email"] == "alice@example.com"


def test_create_service_without_responsibles(client):
    payload = {"name": "Simple Service"}
    resp = client.post("/api/v1/services", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["responsibles"] == []


def test_create_service_default_sla(client):
    payload = {"name": "Default SLA Service"}
    resp = client.post("/api/v1/services", json=payload)
    data = resp.json()
    assert float(data["slaTargetPercent"]) == 99.9


def test_create_service_multiple_responsibles(client):
    payload = {
        "name": "Team Service",
        "responsibles": [
            {"fullName": "Alice", "email": "alice@example.com"},
            {"fullName": "Bob", "email": "bob@example.com"},
        ],
    }
    resp = client.post("/api/v1/services", json=payload)
    assert resp.status_code == 201
    assert len(resp.json()["responsibles"]) == 2


def test_create_service_invalid_email(client):
    payload = {
        "name": "Bad Service",
        "responsibles": [{"fullName": "Alice", "email": "not-an-email"}],
    }
    resp = client.post("/api/v1/services", json=payload)
    assert resp.status_code == 422


def test_create_service_missing_name(client):
    resp = client.post("/api/v1/services", json={})
    assert resp.status_code == 422


def test_list_services_empty(client):
    resp = client.get("/api/v1/services")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []


def test_list_services_after_create(client, service_payload):
    client.post("/api/v1/services", json=service_payload)
    resp = client.get("/api/v1/services")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


def test_list_services_multiple(client, service_payload):
    client.post("/api/v1/services", json=service_payload)
    client.post("/api/v1/services", json={"name": "Another Service"})
    resp = client.get("/api/v1/services")
    assert len(resp.json()["items"]) == 2


def test_get_service_by_id(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == service_id


def test_get_service_not_found(client):
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/services/{fake_id}")
    assert resp.status_code == 404


def test_get_service_invalid_uuid(client):
    resp = client.get("/api/v1/services/not-a-uuid")
    assert resp.status_code == 422


def test_service_id_is_uuid(client, service_payload):
    resp = client.post("/api/v1/services", json=service_payload)
    service_id = resp.json()["id"]
    try:
        uuid.UUID(service_id)
    except ValueError:
        assert False, f"id is not a valid UUID: {service_id}"
