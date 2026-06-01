def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_content_type_is_json(client):
    resp = client.get("/health")
    assert "application/json" in resp.headers["content-type"]
