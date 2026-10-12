import os

# Never use the developer's .env or the remote database in tests.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["CA_CERT_PATH"] = ""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import Application, Person
from app.models.auth import Credential
from app.models.person import PersonRole
from app.security import hash_password
from main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine)
    with sessions() as db:
        person = Person(
            firstname="Admin",
            lastname="Test",
            email="admin@example.com",
            role=PersonRole.admin,
        )
        db.add(person)
        db.flush()
        db.add(
            Credential(
                people_id=person.id, password_hash=hash_password("admin-password")
            )
        )
        db.commit()

    def override():
        with sessions() as db:
            yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as client:
        client.sessions = sessions
        yield client
    app.dependency_overrides.clear()
    engine.dispose()


def login(client, email="admin@example.com", password="admin-password"):
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def ad(client, headers, status="published"):
    response = client.post("/companies/", headers=headers, json={"name": "HireLoop"})
    assert response.status_code == 201
    company_id = response.json()["id"]
    response = client.post(
        "/advertisements/",
        headers=headers,
        json={
            "title": "React developer",
            "short_description": "Build a jobboard",
            "full_description": "Full description",
            "company_id": company_id,
            "status": status,
            "salary": "42000.00",
            "location": "Paris",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def register(client, email="user@example.com"):
    payload = {
        "firstname": "Ada",
        "lastname": "Lovelace",
        "email": email,
        "phone": "0600000000",
        "password": "user-password",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text
    assert "password" not in response.json()
    return response.json()


def test_public_board_and_admin_crud(client):
    headers = login(client)
    record = ad(client, headers)
    assert client.get("/health").status_code == 200
    assert client.get("/advertisements/").json()[0]["title"] == "React developer"
    assert (
        client.get(f"/advertisements/{record['id']}").json()["full_description"]
        == "Full description"
    )
    assert (
        client.get(f"/companies/{record['company_id']}/ads").json()[0]["id"]
        == record["id"]
    )
    assert client.get("/advertisements/?limit=1&offset=1").json() == []
    assert client.get("/advertisements/?limit=1000").status_code == 422
    assert client.get("/advertisements/999").status_code == 404
    response = client.patch(
        f"/advertisements/{record['id']}", headers=headers, json={"status": "draft"}
    )
    assert response.status_code == 200
    assert client.get("/advertisements/").json() == []
    assert client.get(f"/advertisements/{record['id']}").status_code == 404
    assert len(client.get("/advertisements/", headers=headers).json()) == 1
    assert (
        client.patch(
            f"/advertisements/{record['id']}", headers=headers, json={"title": None}
        ).status_code
        == 422
    )
    assert (
        client.delete(f"/advertisements/{record['id']}", headers=headers).status_code
        == 204
    )


def test_auth_profile_and_revocation(client):
    person = register(client)
    headers = login(client, "user@example.com", "user-password")
    assert client.get("/auth/me", headers=headers).json()["id"] == person["id"]
    assert (
        client.patch("/auth/me", headers=headers, json={"firstname": "Grace"}).json()[
            "firstname"
        ]
        == "Grace"
    )
    assert (
        client.patch("/auth/me", headers=headers, json={"role": "admin"}).status_code
        == 422
    )
    assert (
        client.patch("/auth/me", headers=headers, json={"email": None}).status_code
        == 422
    )
    assert (
        client.post(
            "/auth/login", json={"email": "user@example.com", "password": "wrong"}
        ).status_code
        == 401
    )
    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/auth/me", headers=headers).status_code == 401
    with client.sessions() as db:
        assert db.get(Credential, person["id"]).password_hash != "user-password"


def test_authorization_and_validation(client):
    register(client)
    user = login(client, "user@example.com", "user-password")
    for resource in ["companies", "people", "applications"]:
        assert client.get(f"/{resource}/").status_code == 401
        assert client.get(f"/{resource}/", headers=user).status_code == 403
        assert client.post(f"/{resource}/", headers=user, json={}).status_code == 403
        assert client.patch(f"/{resource}/1", headers=user, json={}).status_code == 403
        assert client.delete(f"/{resource}/1", headers=user).status_code == 403
    assert client.post("/advertisements/", headers=user, json={}).status_code == 403
    admin = login(client)
    assert client.post("/companies/", headers=admin, json={}).status_code == 400
    assert (
        client.post(
            "/advertisements/",
            headers=admin,
            json={
                "title": "Test",
                "short_description": "Test",
                "full_description": "Test",
                "company_id": 999,
            },
        ).status_code
        == 404
    )
    assert client.delete("/people/1", headers=admin).status_code == 409
    assert (
        client.patch(
            "/auth/me", headers=user, json={"email": "admin@example.com"}
        ).status_code
        == 409
    )
    assert client.get("/auth/me", headers=user).json()["email"] == "user@example.com"


def test_authenticated_and_guest_applications(client):
    admin = login(client)
    record = ad(client, admin)
    person = register(client)
    user = login(client, "user@example.com", "user-password")
    path = f"/advertisements/{record['id']}/applications"
    response = client.post(path, headers=user, json={"message": "Interested!"})
    assert response.status_code == 201, response.text
    application = response.json()
    assert application["people_id"] == person["id"]
    assert client.post(path, headers=user, json={"message": "Again"}).status_code == 409
    assert client.post(path, json={"message": "Missing details"}).status_code == 400
    guest = {
        "firstname": "Guest",
        "lastname": "Test",
        "email": "guest@example.com",
        "message": "Hello",
    }
    assert client.post(path, json=guest).status_code == 201
    assert (
        client.post(path, json={**guest, "email": "user@example.com"}).status_code
        == 409
    )
    assert (
        client.post(
            path, json={"people_id": person["id"], "message": "Impersonation"}
        ).status_code
        == 422
    )
    with client.sessions() as db:
        assert len(db.scalars(select(Application)).all()) == 2
    assert (
        client.patch(
            f"/applications/{application['id']}",
            headers=admin,
            json={"status": "accepted"},
        ).json()["status"]
        == "accepted"
    )
    # Database cascades work locally as well as on MySQL.
    assert (
        client.delete(f"/companies/{record['company_id']}", headers=admin).status_code
        == 204
    )
    assert client.get("/applications/", headers=admin).json() == []


def test_remaining_admin_resources(client):
    admin = login(client)
    record = ad(client, admin)
    person = client.post(
        "/people/",
        headers=admin,
        json={"firstname": "Test", "lastname": "Person", "email": "person@example.com"},
    ).json()
    assert client.get(f"/people/{person['id']}", headers=admin).status_code == 200
    assert (
        client.patch(
            f"/people/{person['id']}", headers=admin, json={"phone": "123"}
        ).json()["phone"]
        == "123"
    )
    assert (
        client.patch(
            f"/people/{person['id']}", headers=admin, json={"firstname": None}
        ).status_code
        == 422
    )
    assert (
        client.get(f"/companies/{record['company_id']}", headers=admin).status_code
        == 200
    )
    assert (
        client.patch(
            f"/companies/{record['company_id']}", headers=admin, json={"city": "Lyon"}
        ).json()["city"]
        == "Lyon"
    )
    response = client.post(
        "/applications/",
        headers=admin,
        json={
            "people_id": person["id"],
            "advertisement_id": record["id"],
            "message": "Test",
        },
    )
    assert response.status_code == 201
    application = response.json()
    assert (
        client.get(f"/applications/{application['id']}", headers=admin).status_code
        == 200
    )
    assert (
        client.delete(f"/applications/{application['id']}", headers=admin).status_code
        == 204
    )
    assert client.delete(f"/people/{person['id']}", headers=admin).status_code == 204
    assert client.get(f"/people/{person['id']}", headers=admin).status_code == 404


def test_expired_session(client):
    from datetime import timedelta

    from app.clock import utcnow
    from app.models.auth import AuthSession

    headers = login(client)
    with client.sessions() as db:
        session = db.scalar(select(AuthSession))
        session.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert client.get("/auth/me", headers=headers).status_code == 401
