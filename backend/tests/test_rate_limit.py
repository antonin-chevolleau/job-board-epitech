import pytest
from app.api.rate_limit import limiter
from app.core.config import Settings, settings
from app.core.rate_limit import SlidingWindowLimiter, parse_rate
from app.main import app
from fastapi.testclient import TestClient
from pydantic import ValidationError

DB = "mysql+pymysql://u:p@localhost/db"
KEY = "a1b2" * 16


@pytest.fixture
def limits_on(monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_login", "3/minute")
    monkeypatch.setattr(settings, "rate_limit_apply", "2/hour")
    limiter.clear()
    yield
    limiter.clear()


def _login(client, password="wrong"):
    return client.post(
        "/api/auth/login", data={"username": "admin", "password": password}
    )


# --- unit: parsing and sliding window ------------------------------------------


@pytest.mark.parametrize(
    ("rate", "expected"),
    [
        ("10/minute", (10, 60)),
        ("5/second", (5, 1)),
        ("20/hour", (20, 3600)),
        ("1/DAY", (1, 86400)),
    ],
)
def test_parse_rate(rate, expected):
    assert parse_rate(rate) == expected


@pytest.mark.parametrize(
    "rate", ["", "10", "ten/minute", "10/week", "0/minute", "-1/hour"]
)
def test_parse_rate_rejects_malformed(rate):
    with pytest.raises(ValueError):
        parse_rate(rate)


def test_sliding_window():
    now = [100.0]
    store = SlidingWindowLimiter(clock=lambda: now[0])
    assert store.hit("k", 2, 60) is None
    now[0] += 10
    assert store.hit("k", 2, 60) is None
    now[0] += 10
    assert store.hit("k", 2, 60) == 40  # oldest hit leaves the window at t=160
    assert store.hit("other", 2, 60) is None  # keys are independent
    now[0] += 41
    assert store.hit("k", 2, 60) is None  # window slid
    now[0] += 1000
    assert store.hit("k", 2, 60) is None and store.hit("k", 2, 60) is None


def test_invalid_rate_in_settings_is_rejected():
    with pytest.raises(ValidationError):
        Settings(database_url=DB, secret_key=KEY, rate_limit_login="fast")
    assert Settings(database_url=DB, secret_key=KEY).rate_limit_login == "10/minute"


# --- API ----------------------------------------------------------------------


def test_login_is_rate_limited(limits_on, client):
    assert [_login(client).status_code for _ in range(3)] == [401, 401, 401]
    blocked = _login(client)
    assert blocked.status_code == 429
    assert 1 <= int(blocked.headers["retry-after"]) <= 60
    # even the right password is refused while blocked
    assert _login(client, "admin1234").status_code == 429


def test_limit_is_per_client_ip(limits_on, client):
    for _ in range(4):
        _login(client)
    assert _login(client).status_code == 429
    with TestClient(app, client=("203.0.113.7", 50000)) as other:
        assert _login(other, "admin1234").status_code == 200


def test_application_is_rate_limited_even_when_invalid(limits_on, client):
    url = "/api/advertisements/1/applications"
    # invalid bodies are rejected with 422 but still count
    assert client.post(url, json={"message": ""}).status_code == 422
    assert client.post(url, json={"message": ""}).status_code == 422
    r = client.post(url, json={"message": ""})
    assert r.status_code == 429 and "retry-after" in r.headers


def test_login_and_apply_have_separate_budgets(limits_on, client):
    for _ in range(4):
        _login(client)
    assert _login(client).status_code == 429
    r = client.post("/api/advertisements/1/applications", json={"message": ""})
    assert r.status_code == 422


def test_other_routes_are_not_limited(limits_on, client):
    for _ in range(10):
        assert client.get("/api/advertisements").status_code == 200


def test_disabled_limiter_lets_everything_through(client, monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_login", "1/minute")
    assert [_login(client).status_code for _ in range(5)] == [401] * 5
