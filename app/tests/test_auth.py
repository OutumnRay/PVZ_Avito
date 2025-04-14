import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_dummy_login_success():
    response = client.post("/auth/dummyLogin", json={"role": "employee"})
    assert response.status_code == 200
    assert "token" in response.json()


def test_dummy_login_invalid_role():
    response = client.post("/auth/dummyLogin", json={"role": "guest"})
    assert response.status_code == 400


def test_register_and_login(monkeypatch):
    def fake_get_connection():
        class Cursor:
            def execute(self, query, params): pass
            def fetchone(self): return ["user-id", "user@test.com", "employee"]
            def __enter__(self): return self
            def __exit__(self, *args): pass

        class Conn:
            def cursor(self): return Cursor()
            def __enter__(self): return self
            def __exit__(self, *args): pass

        return Conn()

    monkeypatch.setattr("routes.auth.get_connection", fake_get_connection)

    response = client.post("/auth/register", json={
        "email": "user@test.com",
        "password": "123",
        "role": "employee"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "user@test.com"

    response = client.post("/auth/login", json={
        "email": "user@test.com",
        "password": "123"
    })
    assert response.status_code == 200
    assert "token" in response.json()
