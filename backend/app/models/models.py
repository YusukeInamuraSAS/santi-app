from datetime import datetime
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base


class MoodLevel(str, enum.Enum):
    very_bad = "very_bad"
    bad = "bad"
    neutral = "neutral"
    good = "good"
    very_good = "very_good"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーション
    mood_records: Mapped[list["MoodRecord"]] = relationship("MoodRecord", back_populates="user", cascade="all, delete-orphan")
    practice_logs: Mapped[list["PracticeLog"]] = relationship("PracticeLog", back_populates="user", cascade="all, delete-orphan")
    user_values: Mapped[list["UserValue"]] = relationship("UserValue", back_populates="user", cascade="all, delete-orphan")


class Value(Base):
    """価値観マスター（執着を手放すための行動指針）"""
    __tablename__ = "values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # 例: peace, compassion, wisdom
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user_values: Mapped[list["UserValue"]] = relationship("UserValue", back_populates="value")


class UserValue(Base):
    """ユーザーが選んだ価値観"""
    __tablename__ = "user_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    value_id: Mapped[int] = mapped_column(Integer, ForeignKey("values.id"), nullable=False)
    selected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="user_values")
    value: Mapped["Value"] = relationship("Value", back_populates="user_values")


class MoodRecord(Base):
    """日々の気分記録"""
    __tablename__ = "mood_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    mood: Mapped[MoodLevel] = mapped_column(Enum(MoodLevel), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 1.0〜5.0
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="mood_records")


class DailyPractice(Base):
    """今日のおすすめの実践（一歩）マスター"""
    __tablename__ = "daily_practices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=5)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    logs: Mapped[list["PracticeLog"]] = relationship("PracticeLog", back_populates="practice")


class PracticeLog(Base):
    """実践記録（ユーザーの行動ログ）"""
    __tablename__ = "practice_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    practice_id: Mapped[int] = mapped_column(Integer, ForeignKey("daily_practices.id"), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    reflection: Mapped[str | None] = mapped_column(Text, nullable=True)  # 振り返りメモ
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="practice_logs")
    practice: Mapped["DailyPractice"] = relationship("DailyPractice", back_populates="logs")
