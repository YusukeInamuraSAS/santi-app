from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.db import init_db
from app.api.auth import router as auth_router
from app.api.moods import router as moods_router
from app.api.practices import values_router, practices_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS（Vercel / localhost 両対応）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth_router)
app.include_router(moods_router)
app.include_router(values_router)
app.include_router(practices_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
