from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.models.models import User, MoodRecord
from app.schemas.schemas import MoodCreate, MoodResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/moods", tags=["気分記録"])


@router.post("/", response_model=MoodResponse, status_code=201)
async def create_mood(
    payload: MoodCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """気分を記録する"""
    record = MoodRecord(
        user_id=current_user.id,
        mood=payload.mood,
        note=payload.note,
        score=payload.score,
    )
    db.add(record)
    await db.flush()
    return record


@router.get("/", response_model=list[MoodResponse])
async def get_moods(
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """自分の気分記録一覧（最新順）"""
    result = await db.execute(
        select(MoodRecord)
        .where(MoodRecord.user_id == current_user.id)
        .order_by(desc(MoodRecord.recorded_at))
        .limit(limit)
    )
    return result.scalars().all()


@router.delete("/{mood_id}", status_code=204)
async def delete_mood(
    mood_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """気分記録を削除する"""
    result = await db.execute(
        select(MoodRecord).where(MoodRecord.id == mood_id, MoodRecord.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    await db.delete(record)
