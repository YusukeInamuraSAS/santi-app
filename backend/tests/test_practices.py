import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestValues:
    async def test_list_values(self, client: AsyncClient):
        resp = await client.get("/api/values/")
        assert resp.status_code == 200
        values = resp.json()
        assert len(values) >= 3
        assert any(v["name"] == "平和" for v in values)

    async def test_add_and_get_my_values(self, auth_client: AsyncClient):
        # 価値観ID=1を選択
        resp = await auth_client.post("/api/values/me", json={"value_id": 1})
        assert resp.status_code == 201
        assert resp.json()["value_id"] == 1

        # 一覧取得
        list_resp = await auth_client.get("/api/values/me")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

    async def test_duplicate_value_selection(self, auth_client: AsyncClient):
        await auth_client.post("/api/values/me", json={"value_id": 1})
        resp = await auth_client.post("/api/values/me", json={"value_id": 1})
        assert resp.status_code == 400
        assert "既に選択済み" in resp.json()["detail"]

    async def test_remove_my_value(self, auth_client: AsyncClient):
        await auth_client.post("/api/values/me", json={"value_id": 2})
        resp = await auth_client.delete("/api/values/me/2")
        assert resp.status_code == 204

        list_resp = await auth_client.get("/api/values/me")
        assert all(v["value_id"] != 2 for v in list_resp.json())


@pytest.mark.asyncio
class TestPractices:
    async def test_list_practices(self, client: AsyncClient):
        resp = await client.get("/api/practices/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    async def test_log_practice(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/practices/logs", json={
            "practice_id": 1,
            "completed": True,
            "reflection": "呼吸に集中できて、心が落ち着きました",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["completed"] is True
        assert data["practice"]["title"] == "3分間の呼吸瞑想"

    async def test_get_practice_logs(self, auth_client: AsyncClient):
        await auth_client.post("/api/practices/logs", json={"practice_id": 1, "completed": True})
        await auth_client.post("/api/practices/logs", json={"practice_id": 2, "completed": False})

        resp = await auth_client.get("/api/practices/logs")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    async def test_practice_log_requires_auth(self, client: AsyncClient):
        resp = await client.post("/api/practices/logs", json={"practice_id": 1})
        assert resp.status_code == 401
