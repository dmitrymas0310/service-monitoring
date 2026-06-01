import uuid


def test_create_endpoint_returns_201(client, created_service, endpoint_payload):
    service_id = created_service["id"]
    resp = client.post(f"/api/v1/services/{service_id}/endpoints", json=endpoint_payload)
    assert resp.status_code == 201


def test_create_endpoint_response_fields(client, created_service, endpoint_payload):
    service_id = created_service["id"]
    resp = client.post(f"/api/v1/services/{service_id}/endpoints", json=endpoint_payload)
    data = resp.json()
    assert "id" in data
    assert data["serviceId"] == service_id
    assert data["name"] == endpoint_payload["name"]
    assert data["url"] == endpoint_payload["url"]
    assert data["method"] == "GET"
    assert data["timeoutMs"] == endpoint_payload["timeoutMs"]
    assert data["checkIntervalSec"] == endpoint_payload["checkIntervalSec"]
    assert data["isActive"] is True
    assert "createdAt" in data
    assert "updatedAt" in data


def test_create_endpoint_default_values(client, created_service):
    service_id = created_service["id"]
    payload = {"name": "Minimal", "url": "http://example.com/health"}
    resp = client.post(f"/api/v1/services/{service_id}/endpoints", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["method"] == "GET"
    assert data["timeoutMs"] == 2000
    assert data["checkIntervalSec"] == 10
    assert data["isActive"] is True


def test_create_endpoint_non_get_method_rejected(client, created_service):
    service_id = created_service["id"]
    payload = {"name": "POST ep", "url": "http://example.com", "method": "POST"}
    resp = client.post(f"/api/v1/services/{service_id}/endpoints", json=payload)
    assert resp.status_code == 422


def test_create_endpoint_service_not_found(client, endpoint_payload):
    fake_id = str(uuid.uuid4())
    resp = client.post(f"/api/v1/services/{fake_id}/endpoints", json=endpoint_payload)
    assert resp.status_code == 404


def test_create_endpoint_missing_url(client, created_service):
    service_id = created_service["id"]
    resp = client.post(
        f"/api/v1/services/{service_id}/endpoints", json={"name": "No URL"}
    )
    assert resp.status_code == 422


def test_list_endpoints_empty(client, created_service):
    service_id = created_service["id"]
    resp = client.get(f"/api/v1/services/{service_id}/endpoints")
    assert resp.status_code == 200
    assert resp.json()["items"] == []


def test_list_endpoints_after_create(client, created_service, endpoint_payload):
    service_id = created_service["id"]
    client.post(f"/api/v1/services/{service_id}/endpoints", json=endpoint_payload)
    resp = client.get(f"/api/v1/services/{service_id}/endpoints")
    assert len(resp.json()["items"]) == 1


def test_list_endpoints_multiple(client, created_service, endpoint_payload):
    service_id = created_service["id"]
    client.post(f"/api/v1/services/{service_id}/endpoints", json=endpoint_payload)
    second = dict(endpoint_payload, name="Second EP", url="http://example.com/status")
    client.post(f"/api/v1/services/{service_id}/endpoints", json=second)
    resp = client.get(f"/api/v1/services/{service_id}/endpoints")
    assert len(resp.json()["items"]) == 2


def test_list_endpoints_service_not_found(client):
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/services/{fake_id}/endpoints")
    assert resp.status_code == 404


def test_get_endpoint_by_id(client, created_endpoint):
    endpoint_id = created_endpoint["id"]
    resp = client.get(f"/api/v1/endpoints/{endpoint_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == endpoint_id


def test_get_endpoint_not_found(client):
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/endpoints/{fake_id}")
    assert resp.status_code == 404


def test_patch_endpoint_url(client, created_endpoint):
    endpoint_id = created_endpoint["id"]
    new_url = "http://new-host.example.com/health"
    resp = client.patch(f"/api/v1/endpoints/{endpoint_id}", json={"url": new_url})
    assert resp.status_code == 200
    assert resp.json()["url"] == new_url


def test_patch_endpoint_timeout(client, created_endpoint):
    endpoint_id = created_endpoint["id"]
    resp = client.patch(
        f"/api/v1/endpoints/{endpoint_id}", json={"timeoutMs": 5000}
    )
    assert resp.status_code == 200
    assert resp.json()["timeoutMs"] == 5000


def test_patch_endpoint_deactivate(client, created_endpoint):
    endpoint_id = created_endpoint["id"]
    resp = client.patch(
        f"/api/v1/endpoints/{endpoint_id}", json={"isActive": False}
    )
    assert resp.status_code == 200
    assert resp.json()["isActive"] is False


def test_patch_endpoint_not_found(client):
    fake_id = str(uuid.uuid4())
    resp = client.patch(f"/api/v1/endpoints/{fake_id}", json={"url": "http://x.com"})
    assert resp.status_code == 404


def test_patch_endpoint_partial_update_preserves_other_fields(client, created_endpoint):
    endpoint_id = created_endpoint["id"]
    original_url = created_endpoint["url"]
    resp = client.patch(
        f"/api/v1/endpoints/{endpoint_id}", json={"timeoutMs": 9000}
    )
    assert resp.json()["url"] == original_url
    assert resp.json()["timeoutMs"] == 9000
