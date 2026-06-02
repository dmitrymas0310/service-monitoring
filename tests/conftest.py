import os
from pathlib import Path

# Если DATABASE_URL уже указывает на PostgreSQL (например, в Docker) — используем его.
# Иначе — поднимаем SQLite in-memory для локального запуска.
_existing_url = os.environ.get("DATABASE_URL", "")
_USE_POSTGRES = _existing_url.startswith("postgresql")

if not _USE_POSTGRES:
    _TEST_DIR = Path(__file__).parent
    _DB_URL = f"sqlite:///{_TEST_DIR / 'test_monitoring.db'}"
    os.environ["DATABASE_URL"] = _DB_URL
else:
    _DB_URL = _existing_url

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

if _USE_POSTGRES:
    _engine = create_engine(_DB_URL)
else:
    _engine = create_engine(
        _DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)
    if not _USE_POSTGRES:
        _engine.dispose()
        db_file = Path(__file__).parent / "test_monitoring.db"
        if db_file.exists():
            db_file.unlink()


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = _TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture
def db():
    session = _TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


SERVICE_PAYLOAD = {
    "name": "Payment Service",
    "description": "Handles payment processing",
    "slaTargetPercent": "99.50",
    "responsibles": [
        {"fullName": "Alice Smith", "email": "alice@example.com"},
    ],
}

ENDPOINT_PAYLOAD = {
    "name": "Health Check",
    "url": "http://payment-service/health",
    "method": "GET",
    "timeoutMs": 3000,
    "checkIntervalSec": 30,
    "isActive": True,
}


@pytest.fixture
def service_payload():
    return dict(SERVICE_PAYLOAD)


@pytest.fixture
def endpoint_payload():
    return dict(ENDPOINT_PAYLOAD)


@pytest.fixture
def created_service(client, service_payload):
    resp = client.post("/api/v1/services", json=service_payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def created_endpoint(client, created_service, endpoint_payload):
    service_id = created_service["id"]
    resp = client.post(
        f"/api/v1/services/{service_id}/endpoints", json=endpoint_payload
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def insert_check_result(db, service_id, endpoint_id, status="UP", checked_at=None):
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.repositories.check_result_repository import create_check_result

    if isinstance(service_id, str):
        service_id = _uuid.UUID(service_id)
    if isinstance(endpoint_id, str):
        endpoint_id = _uuid.UUID(endpoint_id)

    data = {
        "service_id": service_id,
        "endpoint_id": endpoint_id,
        "checked_at": checked_at or datetime.now(timezone.utc),
        "status": status,
        "http_status_code": 200 if status == "UP" else 503,
        "latency_ms": 50 if status == "UP" else None,
        "error_type": None if status == "UP" else "HTTP_5XX",
        "error_message": None if status == "UP" else "HTTP 503",
    }
    return create_check_result(db, data)
