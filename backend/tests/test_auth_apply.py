import pytest
from app.services import emailer


@pytest.fixture
def sent_emails(monkeypatch):
    """Capture outgoing emails instead of using SMTP."""
    sent = []

    def fake_send(to, subject, body, reply_to=None):
        sent.append({"to": to, "subject": subject, "body": body, "reply_to": reply_to})
        return True

    monkeypatch.setattr(emailer, "send_email", fake_send)
    return sent


@pytest.fixture
def new_user(client, cleanup, uid):
    """Register a fresh user; returns (payload, user, auth headers)."""
    payload = {
        "user_name": f"reg_{uid}",
        "first_name": "Reg",
        "last_name": "Istered",
        "email": f"{uid}@register.example.com",
        "phone": "+33622222222",
        "password": "initialpass1",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 201, r.text
    user = r.json()
    cleanup(f"/api/users/{user['id']}")
    login = client.post(
        "/api/auth/login",
        data={"username": payload["user_name"], "password": payload["password"]},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return payload, user, headers


@pytest.fixture
def fullstack_ad(client):
    """Seeded active ad posted by the recruiter (user 2)."""
    items = client.get("/api/advertisements", params={"q": "Full-Stack"}).json()[
        "items"
    ]
    return client.get(f"/api/advertisements/{items[0]['id']}").json()


# --- register / me ----------------------------------------------------------


def test_register_creates_plain_user(new_user):
    _, user, _ = new_user
    assert user["role"] == "user" and user["company_id"] is None
    assert "password" not in user and "hashed_password" not in user


def test_register_ignores_role_and_rejects_duplicates(client, cleanup, uid):
    payload = {
        "user_name": f"sneaky_{uid}",
        "first_name": "S",
        "last_name": "N",
        "email": f"{uid}@sneaky.example.com",
        "phone": "+33633333333",
        "password": "initialpass1",
        "role": "admin",
        "company_id": 1,
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 201
    cleanup(f"/api/users/{r.json()['id']}")
    assert r.json()["role"] == "user" and r.json()["company_id"] is None

    assert client.post("/api/auth/register", json=payload).status_code == 409
    other = {
        **payload,
        "user_name": f"other_{uid}",
        "email": f"o{uid}@sneaky.example.com",
    }
    assert (
        client.post(
            "/api/auth/register", json={**other, "password": "x" * 100}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/auth/register", json={**other, "password": "short"}
        ).status_code
        == 422
    )


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.put("/api/auth/me", json={}).status_code == 401


def test_me_read_and_update(client, new_user):
    payload, user, headers = new_user
    assert client.get("/api/auth/me", headers=headers).json()["id"] == user["id"]

    profile = {
        k: payload[k]
        for k in ("user_name", "first_name", "last_name", "email", "phone")
    }
    r = client.put(
        "/api/auth/me", json={**profile, "phone": "+33699999999"}, headers=headers
    )
    assert r.status_code == 200 and r.json()["phone"] == "+33699999999"
    assert r.json()["role"] == "user"

    # email already used by another account
    r = client.put(
        "/api/auth/me",
        json={**profile, "email": "admin@jobboard.example"},
        headers=headers,
    )
    assert r.status_code == 409


def test_me_password_change(client, new_user):
    payload, _, headers = new_user
    profile = {
        k: payload[k]
        for k in ("user_name", "first_name", "last_name", "email", "phone")
    }

    no_current = client.put(
        "/api/auth/me",
        json={**profile, "new_password": "brandnewpass1"},
        headers=headers,
    )
    assert no_current.status_code == 400
    wrong = client.put(
        "/api/auth/me",
        json={**profile, "new_password": "brandnewpass1", "current_password": "nope"},
        headers=headers,
    )
    assert wrong.status_code == 400

    ok = client.put(
        "/api/auth/me",
        json={
            **profile,
            "new_password": "brandnewpass1",
            "current_password": payload["password"],
        },
        headers=headers,
    )
    assert ok.status_code == 200
    old = client.post(
        "/api/auth/login",
        data={"username": payload["user_name"], "password": payload["password"]},
    )
    new = client.post(
        "/api/auth/login",
        data={"username": payload["user_name"], "password": "brandnewpass1"},
    )
    assert old.status_code == 401 and new.status_code == 200


# --- public application -------------------------------------------------------


def test_anonymous_application(client, admin, cleanup, uid, fullstack_ad, sent_emails):
    url = f"/api/advertisements/{fullstack_ad['id']}/applications"
    body = {
        "applicant_name": "Visitor Anon",
        "applicant_email": f"{uid}@visitor.example.com",
        "applicant_phone": "+33644444444",
        "message": "I would love to join.",
    }
    # identity is mandatory when not logged in
    r = client.post(url, json={"message": "hi"})
    assert r.status_code == 422 and "name" in r.json()["detail"]

    r = client.post(url, json=body)
    assert r.status_code == 201, r.text
    receipt = r.json()
    cleanup(f"/api/applications/{receipt['id']}")
    assert (
        receipt["status"] == "pending"
        and receipt["applicant_email"] == body["applicant_email"]
    )
    assert "email_sent_at" not in receipt and "user_id" not in receipt

    # persisted, linked to no user, owner notified (background task) and tracked
    stored = client.get(f"/api/applications/{receipt['id']}", headers=admin).json()
    assert stored["user_id"] is None and stored["email_sent_at"] is not None
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "claire.martin@acme-tech.example"  # ad owner
    assert sent_emails[0]["reply_to"] == body["applicant_email"]
    assert fullstack_ad["title"] in sent_emails[0]["subject"]

    # same email, same ad -> conflict
    assert client.post(url, json=body).status_code == 409


def test_application_without_smtp_still_saved(
    client, admin, cleanup, uid, fullstack_ad, monkeypatch
):
    """Without SMTP the application is saved and email_sent_at stays NULL."""
    monkeypatch.setattr(emailer.settings, "smtp_host", None)
    r = client.post(
        f"/api/advertisements/{fullstack_ad['id']}/applications",
        json={
            "applicant_name": "No Smtp",
            "applicant_email": f"{uid}@nosmtp.example.com",
            "applicant_phone": "+33655555555",
            "message": "hello",
        },
    )
    assert r.status_code == 201
    cleanup(f"/api/applications/{r.json()['id']}")
    stored = client.get(f"/api/applications/{r.json()['id']}", headers=admin).json()
    assert stored["email_sent_at"] is None


def test_logged_in_application_prefills_profile(
    client, admin, cleanup, new_user, fullstack_ad, sent_emails
):
    payload, user, headers = new_user
    url = f"/api/advertisements/{fullstack_ad['id']}/applications"
    r = client.post(url, json={"message": "Prefilled please"}, headers=headers)
    assert r.status_code == 201, r.text
    cleanup(f"/api/applications/{r.json()['id']}")
    assert r.json()["applicant_name"] == "Reg Istered"
    assert r.json()["applicant_email"] == payload["email"]
    assert r.json()["applicant_phone"] == payload["phone"]
    stored = client.get(f"/api/applications/{r.json()['id']}", headers=admin).json()
    assert stored["user_id"] == user["id"]

    # one application per user and ad; the email of the account cannot be overridden
    again = client.post(
        url,
        json={"message": "again", "applicant_email": f"x{payload['email']}"},
        headers=headers,
    )
    assert again.status_code == 409


def test_logged_in_application_always_uses_account_email(
    client, cleanup, new_user, fullstack_ad, sent_emails
):
    payload, _, headers = new_user
    r = client.post(
        f"/api/advertisements/{fullstack_ad['id']}/applications",
        json={"message": "hi", "applicant_email": "someone.else@example.com"},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    cleanup(f"/api/applications/{r.json()['id']}")
    assert r.json()["applicant_email"] == payload["email"]


def test_anonymous_cannot_apply_with_account_email(client, new_user, fullstack_ad):
    payload, _, _ = new_user
    r = client.post(
        f"/api/advertisements/{fullstack_ad['id']}/applications",
        json={
            "applicant_name": "Not Me",
            "applicant_email": payload["email"],
            "applicant_phone": "+33600000000",
            "message": "hello",
        },
    )
    assert r.status_code == 409 and "log in" in r.json()["detail"]


def test_user_name_cannot_contain_at_sign(client, uid):
    r = client.post(
        "/api/auth/register",
        json={
            "user_name": f"{uid}@victim.example.com",
            "first_name": "A",
            "last_name": "B",
            "email": f"{uid}@attacker.example.com",
            "phone": "+33600000000",
            "password": "initialpass1",
        },
    )
    assert r.status_code == 422


def test_application_to_missing_or_inactive_ad(client, admin):
    body = {
        "applicant_name": "A",
        "applicant_email": "a@visitor.example.com",
        "applicant_phone": "+33600000000",
        "message": "hello",
    }
    assert (
        client.post("/api/advertisements/999999/applications", json=body).status_code
        == 404
    )
    inactive = client.get(
        "/api/advertisements", params={"is_active": False}, headers=admin
    ).json()["items"][0]
    assert (
        client.post(
            f"/api/advertisements/{inactive['id']}/applications", json=body
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/advertisements/1/applications", json={"message": ""}
        ).status_code
        == 422
    )
