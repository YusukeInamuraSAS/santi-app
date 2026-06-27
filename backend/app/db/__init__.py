from app.db.session import Base, engine


async def init_db():
    """テーブルを全て作成する（開発・テスト用）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """テーブルを全て削除する（テスト用）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
