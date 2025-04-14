import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from routes.product import router
from fastapi import FastAPI
from services.token_service import create_token
from uuid import uuid4


app = FastAPI()
app.include_router(router, prefix="/products", tags=["products"])
client = TestClient(app)

VALID_UUID = "11111111-1111-1111-1111-111111111111"


class TestAddProduct(unittest.TestCase):


    def get_auth_header(self, payload: dict) -> dict:
        token = create_token(payload)
        return {"Authorization": f"Bearer {token}"}


    def test_permission_denied(self):
        headers = self.get_auth_header({"role": "moderator"})
        response = client.post("/products", json={"pvzId": 1, "type": "электроника"}, headers=headers)
        self.assertEqual(response.status_code, 403)


    def test_missing_fields(self):
        headers = self.get_auth_header({"role": "employee"})
        response = client.post("/products", json={"pvzId": 1}, headers=headers)
        self.assertEqual(response.status_code, 400)


    def test_invalid_type(self):
        headers = self.get_auth_header({"role": "employee"})
        response = client.post("/products", json={"pvzId": 1, "type": "еда"}, headers=headers)
        self.assertEqual(response.status_code, 400)


    @patch("routes.product.get_connection")
    def test_no_active_reception(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        headers = self.get_auth_header({"role": "employee"})
        response = client.post("/products", json={"pvzId": 1, "type": "одежда"}, headers=headers)
        self.assertEqual(response.status_code, 400)

    @patch("routes.product.get_connection")
    def test_add_product_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        prod_id = str(uuid4())
        rec_id = str(uuid4())

        mock_cursor.fetchone.side_effect = [(rec_id,), (prod_id, "2025-04-13T19:59:07.516865", "электроника")]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        headers = self.get_auth_header({"role": "employee"})
        response = client.post("/products", json={"pvzId": VALID_UUID, "type": "электроника"}, headers=headers)

        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())