from fastapi.testclient import TestClient
from main import app
from services.token_service import create_token
import uuid


client = TestClient(app)


def get_auth_header(role="moderator"):
    token = create_token({"email": f"{role}@test.com", "role": role})
    return {"Authorization": f"Bearer {token}"}


def test_create_pvz_valid(monkeypatch):
    def mock_get_connection():
        class Cursor:
            def execute(self, *args, **kwargs): pass

            def fetchone(self):
                return [str(uuid.uuid4()), "2024-01-01", "Москва"]

            def __enter__(self): return self

            def __exit__(self, *args): pass

        class Conn:
            def cursor(self): return Cursor()

            def __enter__(self): return self

            def __exit__(self, *args): pass

        return Conn()

    monkeypatch.setattr("routes.pvz.get_connection", mock_get_connection)

    payload = {"city": "Москва"}
    headers = get_auth_header("moderator")
    response = client.post("/pvz/pvz", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.json()["city"] == "Москва"


def test_create_pvz_invalid_city():
    payload = {"city": "Самара"}
    headers = get_auth_header("moderator")
    response = client.post("/pvz/pvz", json=payload, headers=headers)
    assert response.status_code == 400


def test_create_pvz_forbidden():
    payload = {"city": "Москва"}
    headers = get_auth_header("employee")
    response = client.post("/pvz/pvz", json=payload, headers=headers)
    assert response.status_code == 403
