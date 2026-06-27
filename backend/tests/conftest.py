import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.models.models import Value, DailyPractice

# テスト用インメモリSQLite（CI環境）
# 本番に近い環境でテストする場合は下記をPostgreSQL URLに変更する
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """各テスト前にテーブルを再作成し、マスターデータを投入する"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        # 価値観マスター
        session.add_all([
            Value(name="平和", description="心の静けさを大切にする", category="peace"),
            Value(name="慈悲", description="他者への思いやり", category="compassion"),
            Value(name="智慧", description="物事の本質を見抜く力", category="wisdom"),
        ])
        # 実践メニュー
        session.add_all([
            DailyPractice(title="3分間の呼吸瞑想", description="目を閉じ、呼吸に意識を向けます", duration_minutes=3),
            DailyPractice(title="感謝の日記", description="今日あった良いことを3つ書く", duration_minutes=5),
        ])
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """テスト用 AsyncClient"""
    async def override_get_db():
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient):
    """ログイン済み AsyncClient（Authorizationヘッダー付き）"""
    await client.post("/api/auth/register", json={
        "email": "test@santi.app",
        "password": "securepass123",
        "display_name": "テストユーザー",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "test@santi.app",
        "password": "securepass123",
    })
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
