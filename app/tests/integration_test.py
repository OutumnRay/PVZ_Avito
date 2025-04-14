import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_full_flow():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        app.client = client

        mod_token = (await client.post("/auth/dummyLogin", json={"role": "moderator"})).json()["token"]
        emp_token = (await client.post("/auth/dummyLogin", json={"role": "employee"})).json()["token"]

        resp = await client.post("/pvz", json={"city": "Москва"}, headers={"Authorization": f"Bearer {mod_token}"})
        assert resp.status_code == 201
        pvz_id = resp.json()["id"]

        resp = await client.post("/receptions", json={"pvzId": pvz_id}, headers={"Authorization": f"Bearer {emp_token}"})
        assert resp.status_code == 201
        reception_id = resp.json()["id"]

        for _ in range(50):
            product_type = "электроника"
            resp = await client.post(
                "/products",
                json={"pvzId": pvz_id, "type": product_type},
                headers={"Authorization": f"Bearer {emp_token}"}
            )
            assert resp.status_code == 201
            assert resp.json()["type"] == product_type

        # Закрытие приемки
        resp = await client.post(f"/pvz/{pvz_id}/close_last_reception", headers={"Authorization": f"Bearer {emp_token}"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "close"
