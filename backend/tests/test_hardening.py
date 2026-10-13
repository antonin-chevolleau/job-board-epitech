"""Edge cases: stale tokens, full-replacement PUT, out-of-range input, secret key."""

import pytest
from app.core.config import Settings
from app.core.security import create_access_token
from pydantic import ValidationError

# --- invalid / expired tokens must not break public routes -------------------


def test_stale_token_is_treated_as_anonymous_on_public_routes(client, admin):
    stale = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/api/advertisements", headers=stale).status_code == 200
    assert client.get("/api/companies", headers=stale).status_code == 200
    first = client.get("/api/advertisements").json()["items"][0]
    assert (
        client.get(f"/api/advertisements/{first['id']}", headers=stale).status_code
        == 200
    )
    # an anonymous caller never sees inactive ads, even with a stale token
    inactive = client.get(
        "/api/advertisements", params={"is_active": False}, headers=admin
    ).json()["items"][0]
    assert (
        client.get(f"/api/advertisements/{inactive['id']}", headers=stale).status_code
        == 404
    )


def test_token_of_deleted_user_is_anonymous(client):
    orphan = {"Authorization": f"Bearer {create_access_token(2_000_000_000, 'admin')}"}
    assert client.get("/api/advertisements", headers=orphan).status_code == 200


@pytest.mark.parametrize("path", ["/api/auth/me", "/api/users", "/api/applications"])
def test_protected_routes_reject_stale_token(client, path):
    stale = {"Authorization": "Bearer not-a-real-token"}
    r = client.get(path, headers=stale)
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


# --- PUT is a full replacement: nothing is reset by omission -------------------


def test_put_requires_every_field(client, admin):
    user = {
        "user_name": "x_user",
        "first_name": "X",
        "last_name": "Y",
        "email": "x@users.example.com",
        "phone": "+33600000000",
    }
    # role and company_id must be explicit (previously they silently reset)
    assert (
        client.put(
            "/api/users/3", json={**user, "company_id": None}, headers=admin
        ).status_code
        == 422
    )
    assert (
        client.put(
            "/api/users/3", json={**user, "role": "user"}, headers=admin
        ).status_code
        == 422
    )

    company = {
        "name": "N",
        "email": "n@co.example.com",
        "phone": "+33100000000",
        "city": "C",
    }
    r = client.put("/api/companies/1", json=company, headers=admin)
    assert r.status_code == 422
    assert {e["loc"][-1] for e in r.json()["detail"]} == {
        "description",
        "address",
        "country",
    }

    ad = {
        "company_id": 1,
        "title": "t",
        "short_description": "s",
        "full_description": "f",
        "contract_type": "CDI",
    }
    r = client.put("/api/advertisements/1", json=ad, headers=admin)
    assert r.status_code == 422
    assert {e["loc"][-1] for e in r.json()["detail"]} == {
        "user_id",
        "location",
        "salary",
        "working_time",
        "is_active",
    }

    application = {
        "advertisement_id": 1,
        "applicant_name": "A",
        "applicant_email": "a@applicants.example.com",
        "applicant_phone": "+33600000000",
        "message": "m",
    }
    r = client.put("/api/applications/1", json=application, headers=admin)
    assert r.status_code == 422
    assert {e["loc"][-1] for e in r.json()["detail"]} == {"user_id", "status"}


def test_omitting_password_on_user_put_is_allowed(client, admin):
    # password is the one optional field: validation passes (404 = no such user)
    body = {
        "user_name": "ghost",
        "first_name": "G",
        "last_name": "H",
        "email": "ghost@users.example.com",
        "phone": "+33600000000",
        "role": "user",
        "company_id": None,
    }
    assert client.put("/api/users/999999", json=body, headers=admin).status_code == 404


# --- oversized / out-of-range input answers 422, never 500 ---------------------


def test_oversized_text_is_rejected(client, admin, company_payload):
    r = client.post(
        "/api/companies",
        json={**company_payload, "description": "x" * 10_001},
        headers=admin,
    )
    assert r.status_code == 422
    r = client.post(
        "/api/applications",
        json={
            "advertisement_id": 1,
            "applicant_name": "A",
            "applicant_email": "a@applicants.example.com",
            "applicant_phone": "+33600000000",
            "message": "x" * 5_001,
        },
        headers=admin,
    )
    assert r.status_code == 422


def test_out_of_range_ids_and_pages_are_rejected(client, admin, ad_payload):
    r = client.post("/api/advertisements", json=ad_payload(10**12), headers=admin)
    assert r.status_code == 422
    r = client.post("/api/advertisements", json=ad_payload(0), headers=admin)
    assert r.status_code == 422
    assert client.get("/api/advertisements", params={"page": 10**9}).status_code == 422
    assert client.get("/api/advertisements", params={"page": 10**30}).status_code == 422


def test_unknown_company_is_422_not_500(client, admin, ad_payload):
    r = client.post(
        "/api/advertisements", json=ad_payload(2_000_000_000), headers=admin
    )
    assert r.status_code == 422


# --- SECRET_KEY ----------------------------------------------------------------


@pytest.mark.parametrize(
    "key",
    [
        "short",
        "change-me-with-at-least-32-random-characters",  # placeholder of .env.example
        "CHANGE-ME-with-at-least-32-random-characters",
    ],
)
def test_weak_or_placeholder_secret_key_is_rejected(key):
    with pytest.raises(ValidationError):
        Settings(database_url="mysql+pymysql://u:p@localhost/db", secret_key=key)


def test_strong_secret_key_is_accepted():
    Settings(database_url="mysql+pymysql://u:p@localhost/db", secret_key="a1b2" * 16)
