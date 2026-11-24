import pytest

from app.main import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "test-token")
    return create_app().test_client()


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["name"] == "pingboard"


def test_healthz(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_checks_with_token(client):
    res = client.get("/api/checks", headers={"Authorization": "Bearer test-token"})
    assert res.status_code == 200
    assert len(res.get_json()["checks"]) == 4


def test_checks_without_token(client):
    res = client.get("/api/checks")
    assert res.status_code == 401


def test_checks_with_wrong_token(client):
    res = client.get("/api/checks", headers={"Authorization": "Bearer nope"})
    assert res.status_code == 401
