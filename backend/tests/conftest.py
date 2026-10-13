"""API tests run against the database configured in .env (seeded with sql/seed.sql).

Every test cleans up the records it creates.
"""

import uuid

import pytest
from app.api.rate_limit import limiter
from app.core.config import settings
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _no_rate_limit(monkeypatch):
    """Tests log in and apply many times from one IP: limits are off by default
    (tests/test_rate_limit.py turns them on explicitly)."""
    monkeypatch.setattr(settings, "rate_limit_enabled", False)
    limiter.clear()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def _login(client, username, password):
    r = client.post(
        "/api/auth/login", data={"username": username, "password": password}
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin(client):
    return _login(client, "admin", "admin1234")


@pytest.fixture(scope="session")
def plain_user(client):
    return _login(client, "jdoe", "admin1234")


@pytest.fixture
def uid():
    return uuid.uuid4().hex[:8]


@pytest.fixture
def cleanup(client, admin):
    """Register API paths to DELETE (in reverse order) when the test ends."""
    paths: list[str] = []
    yield paths.append
    for path in reversed(paths):
        client.delete(path, headers=admin)


@pytest.fixture
def company_payload(uid):
    return {
        "name": f"Test Co {uid}",
        "email": f"{uid}@testco.example.com",
        "phone": "+33123456789",
        "city": "Nantes",
    }


@pytest.fixture
def ad_payload():
    def make(company_id, **over):
        return {
            "company_id": company_id,
            "title": "Test ad",
            "short_description": "short",
            "full_description": "full description",
            "contract_type": "CDI",
            **over,
        }

    return make
