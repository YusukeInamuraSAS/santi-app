import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/api/auth/register", json={
            "email": "new@santi.app",
            "password": "password123",
            "display_name": "新ユーザー",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@santi.app"
        assert data["display_name"] == "新ユーザー"
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient):
        payload = {"email": "dup@santi.app", "password": "password123", "display_name": "重複"}
        await client.post("/api/auth/register", json=payload)
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "既に登録" in resp.json()["detail"]

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post("/api/auth/register", json={
            "email": "short@santi.app",
            "password": "abc",       # 8文字未満
            "display_name": "テスト",
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "email": "login@santi.app",
            "password": "password123",
            "display_name": "ログインテスト",
        })
        resp = await client.post("/api/auth/login", json={
            "email": "login@santi.app",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "email": "wrong@santi.app",
            "password": "password123",
            "display_name": "テスト",
        })
        resp = await client.post("/api/auth/login", json={
            "email": "wrong@santi.app",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={
            "email": "ghost@santi.app",
            "password": "password123",
        })
        assert resp.status_code == 401
