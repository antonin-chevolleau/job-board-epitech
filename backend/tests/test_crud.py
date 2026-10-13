def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# --- access control ---------------------------------------------------------


def test_write_routes_require_admin(client, plain_user, company_payload):
    assert client.post("/api/companies", json=company_payload).status_code == 401
    r = client.post("/api/companies", json=company_payload, headers=plain_user)
    assert r.status_code == 403
    assert client.get("/api/users").status_code == 401
    assert client.get("/api/users", headers=plain_user).status_code == 403
    assert client.get("/api/applications", headers=plain_user).status_code == 403


# --- advertisements: public reads, filters, pagination ------------------------


def test_public_ads_only_active_and_paginated(client):
    r = client.get("/api/advertisements", params={"limit": 2})
    body = r.json()
    assert r.status_code == 200
    assert len(body["items"]) == 2 and body["limit"] == 2 and body["page"] == 1
    assert body["total"] >= 4
    assert all(item["is_active"] for item in body["items"])
    assert "full_description" not in body["items"][0]
    assert body["items"][0]["company"]["name"]

    page2 = client.get("/api/advertisements", params={"limit": 2, "page": 2}).json()
    assert {i["id"] for i in page2["items"]}.isdisjoint(
        {i["id"] for i in body["items"]}
    )


def test_ads_filters(client):
    stage = client.get("/api/advertisements", params={"contract_type": "Stage"}).json()
    assert stage["total"] >= 1
    assert all(i["contract_type"] == "Stage" for i in stage["items"])
    assert (
        client.get("/api/advertisements", params={"q": "Motion"}).json()["total"] >= 1
    )
    assert (
        client.get("/api/advertisements", params={"location": "Lyon"}).json()["total"]
        >= 1
    )
    assert (
        client.get("/api/advertisements", params={"contract_type": "nope"}).status_code
        == 422
    )
    assert client.get("/api/advertisements", params={"limit": 1000}).status_code == 422


def test_inactive_ad_hidden_from_public(client, admin):
    inactive = client.get(
        "/api/advertisements", params={"is_active": False}, headers=admin
    ).json()["items"]
    assert inactive, "seed contains an inactive ad"
    ad_id = inactive[0]["id"]
    assert client.get(f"/api/advertisements/{ad_id}").status_code == 404
    assert client.get(f"/api/advertisements/{ad_id}", headers=admin).status_code == 200
    # the is_active filter is ignored for anonymous users
    public = client.get("/api/advertisements", params={"is_active": False}).json()
    assert all(i["is_active"] for i in public["items"])


def test_ad_detail_has_full_info(client):
    first = client.get("/api/advertisements").json()["items"][0]
    r = client.get(f"/api/advertisements/{first['id']}")
    assert r.status_code == 200
    assert r.json()["full_description"]
    assert client.get("/api/advertisements/999999").status_code == 404


# --- companies / advertisements / applications lifecycle ----------------------


def test_company_crud_and_conflicts(client, admin, cleanup, company_payload):
    r = client.post("/api/companies", json=company_payload, headers=admin)
    assert r.status_code == 201, r.text
    company = r.json()
    cleanup(f"/api/companies/{company['id']}")

    assert (
        client.post("/api/companies", json=company_payload, headers=admin).status_code
        == 409
    )
    assert (
        client.get(f"/api/companies/{company['id']}").json()["name"]
        == company_payload["name"]
    )

    updated = {
        **company_payload,
        "city": "Rennes",
        "description": None,
        "address": None,
        "country": None,
    }
    r = client.put(f"/api/companies/{company['id']}", json=updated, headers=admin)
    assert r.status_code == 200 and r.json()["city"] == "Rennes"

    bad = {**updated, "email": "not-an-email"}
    assert (
        client.put(
            f"/api/companies/{company['id']}", json=bad, headers=admin
        ).status_code
        == 422
    )

    assert (
        client.delete(f"/api/companies/{company['id']}", headers=admin).status_code
        == 204
    )
    assert client.get(f"/api/companies/{company['id']}").status_code == 404
    assert (
        client.delete(f"/api/companies/{company['id']}", headers=admin).status_code
        == 404
    )


def test_ad_crud_and_cascade(client, admin, cleanup, company_payload, ad_payload, uid):
    company = client.post("/api/companies", json=company_payload, headers=admin).json()
    cleanup(f"/api/companies/{company['id']}")

    r = client.post(
        "/api/advertisements",
        json=ad_payload(company["id"], salary=1234.5),
        headers=admin,
    )
    assert r.status_code == 201, r.text
    ad = r.json()
    assert ad["user_id"] == 1  # defaults to the authenticated admin
    assert ad["salary"] == 1234.5 and ad["company"]["id"] == company["id"]

    r = client.put(
        f"/api/advertisements/{ad['id']}",
        json=ad_payload(
            company["id"],
            title="Renamed",
            is_active=False,
            user_id=None,
            location=None,
            salary=None,
            working_time=None,
        ),
        headers=admin,
    )
    assert r.status_code == 200 and r.json()["title"] == "Renamed"

    assert (
        client.post(
            "/api/advertisements", json=ad_payload(999999), headers=admin
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/advertisements",
            json=ad_payload(company["id"], contract_type="X"),
            headers=admin,
        ).status_code
        == 422
    )

    app_payload = {
        "advertisement_id": ad["id"],
        "applicant_name": "Jane Roe",
        "applicant_email": f"{uid}@applicant.example.com",
        "applicant_phone": "+33600000099",
        "message": "Hello",
    }
    r = client.post("/api/applications", json=app_payload, headers=admin)
    assert r.status_code == 201, r.text
    application = r.json()
    assert application["status"] == "pending" and application["email_sent_at"] is None
    # same applicant, same ad -> conflict
    assert (
        client.post("/api/applications", json=app_payload, headers=admin).status_code
        == 409
    )

    r = client.put(
        f"/api/applications/{application['id']}",
        json={**app_payload, "user_id": None, "status": "accepted"},
        headers=admin,
    )
    assert r.status_code == 200 and r.json()["status"] == "accepted"
    listed = client.get(
        "/api/applications",
        params={"advertisement_id": ad["id"], "status": "accepted"},
        headers=admin,
    ).json()
    assert listed["total"] == 1

    # deleting the company cascades to ads and applications
    assert (
        client.delete(f"/api/companies/{company['id']}", headers=admin).status_code
        == 204
    )
    assert (
        client.get(f"/api/applications/{application['id']}", headers=admin).status_code
        == 404
    )
    assert (
        client.get(f"/api/advertisements/{ad['id']}", headers=admin).status_code == 404
    )


# --- users --------------------------------------------------------------------


def test_user_crud(client, admin, cleanup, uid):
    payload = {
        "user_name": f"u_{uid}",
        "first_name": "Test",
        "last_name": "User",
        "email": f"{uid}@users.example.com",
        "phone": "+33611111111",
        "password": "s3cretpass",
    }
    r = client.post("/api/users", json=payload, headers=admin)
    assert r.status_code == 201, r.text
    user = r.json()
    cleanup(f"/api/users/{user['id']}")
    assert "password" not in user and "hashed_password" not in user
    assert user["role"] == "user"

    assert client.post("/api/users", json=payload, headers=admin).status_code == 409
    assert (
        client.post(
            "/api/users",
            json={**payload, "user_name": f"v_{uid}", "password": "x" * 100},
            headers=admin,
        ).status_code
        == 422
    )

    login = client.post(
        "/api/auth/login",
        data={"username": payload["user_name"], "password": "s3cretpass"},
    )
    assert login.status_code == 200 and login.json()["role"] == "user"

    changed = {k: v for k, v in payload.items() if k != "password"} | {
        "role": "recruiter",
        "company_id": None,
    }
    r = client.put(f"/api/users/{user['id']}", json=changed, headers=admin)
    assert r.status_code == 200 and r.json()["role"] == "recruiter"
    # password untouched when omitted
    assert (
        client.post(
            "/api/auth/login",
            data={"username": payload["user_name"], "password": "s3cretpass"},
        ).status_code
        == 200
    )

    found = client.get("/api/users", params={"q": uid}, headers=admin).json()
    assert found["total"] == 1

    assert client.delete(f"/api/users/{user['id']}", headers=admin).status_code == 204
    assert client.get(f"/api/users/{user['id']}", headers=admin).status_code == 404


def test_admin_cannot_delete_or_demote_self(client, admin):
    me = client.get(
        "/api/users", params={"q": "admin", "role": "admin"}, headers=admin
    ).json()["items"][0]
    assert client.delete(f"/api/users/{me['id']}", headers=admin).status_code == 400
    body = {
        k: me[k]
        for k in (
            "user_name",
            "first_name",
            "last_name",
            "email",
            "phone",
            "company_id",
        )
    }
    r = client.put(
        f"/api/users/{me['id']}", json={**body, "role": "user"}, headers=admin
    )
    assert r.status_code == 400
