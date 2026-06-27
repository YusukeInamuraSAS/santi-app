import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMoods:
    async def test_create_mood(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/moods/", json={
            "mood": "good",
            "note": "今日は穏やかな気持ちです",
            "score": 4.0,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["mood"] == "good"
        assert data["note"] == "今日は穏やかな気持ちです"
        assert data["score"] == 4.0

    async def test_create_mood_without_note(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/moods/", json={"mood": "neutral"})
        assert resp.status_code == 201
        assert resp.json()["note"] is None

    async def test_list_moods(self, auth_client: AsyncClient):
        # 複数記録
        for mood in ["good", "very_good", "neutral"]:
            await auth_client.post("/api/moods/", json={"mood": mood})

        resp = await auth_client.get("/api/moods/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 3

    async def test_moods_require_auth(self, client: AsyncClient):
        resp = await client.get("/api/moods/")
        assert resp.status_code == 401

    async def test_delete_mood(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/moods/", json={"mood": "bad"})
        mood_id = create_resp.json()["id"]

        del_resp = await auth_client.delete(f"/api/moods/{mood_id}")
        assert del_resp.status_code == 204

    async def test_delete_other_users_mood(self, auth_client: AsyncClient):
        """他ユーザーの記録は削除できない"""
        # ユーザーAの記録を作成
        create = await auth_client.post("/api/moods/", json={"mood": "good"})
        mood_id = create.json()["id"]

        # ユーザーBを作成してログイン
        await auth_client.post("/api/auth/register", json={
            "email": "other2@santi.app",
            "password": "password123",
            "display_name": "他者",
        })
        login = await auth_client.post("/api/auth/login", json={
            "email": "other2@santi.app", "password": "password123"
        })
        other_token = login.json()["access_token"]

        # ユーザーBとして削除を試みる（ヘッダーを一時的に切替）
        original_headers = dict(auth_client.headers)
        auth_client.headers.update({"Authorization": f"Bearer {other_token}"})
        resp = await auth_client.delete(f"/api/moods/{mood_id}")
        auth_client.headers.update(original_headers)  # 元に戻す

        assert resp.status_code == 404

    async def test_invalid_score(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/moods/", json={"mood": "good", "score": 6.0})
        assert resp.status_code == 422
