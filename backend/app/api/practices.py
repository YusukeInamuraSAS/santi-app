from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.models import User, Value, UserValue, DailyPractice, PracticeLog
from app.schemas.schemas import (
    ValueResponse, UserValueCreate, UserValueResponse,
    PracticeResponse, PracticeLogCreate, PracticeLogResponse,
)
from app.services.auth import get_current_user

values_router = APIRouter(prefix="/api/values", tags=["価値観"])
practices_router = APIRouter(prefix="/api/practices", tags=["実践"])


# ── 価値観 ────────────────────────────────────────
@values_router.get("/", response_model=list[ValueResponse])
async def list_values(db: AsyncSession = Depends(get_db)):
    """価値観マスター一覧"""
    result = await db.execute(select(Value).where(Value.is_active == True))
    return result.scalars().all()


@values_router.get("/me", response_model=list[UserValueResponse])
async def my_values(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """自分が選んだ価値観"""
    result = await db.execute(
        select(UserValue)
        .options(selectinload(UserValue.value))
        .where(UserValue.user_id == current_user.id)
    )
    return result.scalars().all()


@values_router.post("/me", response_model=UserValueResponse, status_code=201)
async def add_my_value(
    payload: UserValueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """価値観を選択する"""
    # 重複チェック
    existing = await db.execute(
        select(UserValue).where(
            UserValue.user_id == current_user.id,
            UserValue.value_id == payload.value_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="既に選択済みの価値観です")

    uv = UserValue(user_id=current_user.id, value_id=payload.value_id)
    db.add(uv)
    await db.flush()
    await db.refresh(uv, ["value"])
    return uv


@values_router.delete("/me/{value_id}", status_code=204)
async def remove_my_value(
    value_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """価値観の選択を解除する"""
    result = await db.execute(
        select(UserValue).where(
            UserValue.user_id == current_user.id,
            UserValue.value_id == value_id,
        )
    )
    uv = result.scalar_one_or_none()
    if not uv:
        raise HTTPException(status_code=404, detail="選択した価値観が見つかりません")
    await db.delete(uv)


# ── 実践 ──────────────────────────────────────────
@practices_router.get("/", response_model=list[PracticeResponse])
async def list_practices(db: AsyncSession = Depends(get_db)):
    """実践メニュー一覧"""
    result = await db.execute(select(DailyPractice).where(DailyPractice.is_active == True))
    return result.scalars().all()


@practices_router.post("/logs", response_model=PracticeLogResponse, status_code=201)
async def log_practice(
    payload: PracticeLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """実践を記録する"""
    log = PracticeLog(
        user_id=current_user.id,
        practice_id=payload.practice_id,
        completed=payload.completed,
        reflection=payload.reflection,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log, ["practice"])
    return log


@practices_router.get("/logs", response_model=list[PracticeLogResponse])
async def my_logs(
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """自分の実践ログ一覧"""
    result = await db.execute(
        select(PracticeLog)
        .options(selectinload(PracticeLog.practice))
        .where(PracticeLog.user_id == current_user.id)
        .limit(limit)
    )
    return result.scalars().all()
