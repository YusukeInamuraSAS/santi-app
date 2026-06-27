from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.models import MoodLevel


# ── Auth ──────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Mood ──────────────────────────────────────────
class MoodCreate(BaseModel):
    mood: MoodLevel
    note: str | None = None
    score: float | None = Field(default=None, ge=1.0, le=5.0)


class MoodResponse(BaseModel):
    id: int
    user_id: int
    mood: MoodLevel
    note: str | None
    score: float | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ── Value ─────────────────────────────────────────
class ValueResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str | None

    model_config = {"from_attributes": True}


class UserValueCreate(BaseModel):
    value_id: int


class UserValueResponse(BaseModel):
    id: int
    value_id: int
    selected_at: datetime
    value: ValueResponse

    model_config = {"from_attributes": True}


# ── Practice ──────────────────────────────────────
class PracticeResponse(BaseModel):
    id: int
    title: str
    description: str
    duration_minutes: int
    category: str | None

    model_config = {"from_attributes": True}


class PracticeLogCreate(BaseModel):
    practice_id: int
    completed: bool = False
    reflection: str | None = None


class PracticeLogResponse(BaseModel):
    id: int
    user_id: int
    practice_id: int
    completed: bool
    reflection: str | None
    logged_at: datetime
    practice: PracticeResponse

    model_config = {"from_attributes": True}
