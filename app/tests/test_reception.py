import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from routes.reception import router
from fastapi import FastAPI
from services.token_service import create_token

app = FastAPI()
app.include_router(router, prefix="/receptions", tags=["reception"])
client = TestClient(app)

VALID_UUID = "11111111-1111-1111-1111-111111111111"

class TestCreateReception(unittest.TestCase):

    def get_auth_header(self, payload: dict) -> dict:
        token = create_token(payload)
        return {"Authorization": f"Bearer {token}"}


    def test_permission_denied(self):
        headers = self.get_auth_header({"role": "moderator"})
        response = client.post("/receptions", json={"pvzId": VALID_UUID}, headers=headers)
        self.assertEqual(response.status_code, 403)


    def test_missing_pvz_id(self):
        headers = self.get_auth_header({"role": "employee"})
        response = client.post("/receptions", json={}, headers=headers)
        self.assertEqual(response.status_code, 400)


    @patch("routes.reception.get_connection")
    def test_open_reception_exists(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [123]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        headers = self.get_auth_header({"role": "employee"})
        response = client.post("/receptions", json={"pvzId": VALID_UUID}, headers=headers)
        self.assertEqual(response.status_code, 400)


    @patch("routes.reception.get_connection")
    def test_create_reception_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            None,
            ("11111111-1111-1111-1111-111111111111", "2025-04-13T19:59:07.516865", "in_progress")  # Новая созданная
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        headers = self.get_auth_header({"role": "employee"})
        response = client.post("/receptions", json={"pvzId": VALID_UUID}, headers=headers)
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["dateTime"], "2025-04-13T19:59:07.516865")
        self.assertEqual(data["status"], "in_progress")
