# Santi - Your Inner Peace Guide

マインドフルネス・メンタルケアアプリのバックエンドAPIです。
「すべては笑顔のために」の精神のもと、心の平穏と前向きな実践をサポートします。

---

## 技術スタック

| 層 | 技術 |
|---|---|
| バックエンド | FastAPI (Python 3.12) |
| データベース | PostgreSQL (Supabase) |
| ORM | SQLAlchemy 2.0 (async) |
| 認証 | JWT (python-jose) |
| マイグレーション | Alembic |
| テスト | pytest + pytest-asyncio |
| フロントエンド | React (Vercel) ※別リポジトリ |

---

## セットアップ

### 1. 環境変数の設定

```bash
cd backend
cp .env.example .env
# .env を編集して DATABASE_URL 等を設定
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. DB マイグレーション

```bash
# Supabase の接続URL を .env に設定後
alembic upgrade head
```

### 4. 開発サーバー起動

```bash
uvicorn app.main:app --reload
```

API ドキュメント: http://localhost:8000/docs

---

## テスト実行

```bash
# 依存追加
pip install aiosqlite

# テスト実行（インメモリSQLite使用のため DB 不要）
pytest

# カバレッジ付き
pytest --cov=app --cov-report=term-missing
```

---

## API エンドポイント一覧

### 認証
| メソッド | パス | 説明 |
|---|---|---|
| POST | /api/auth/register | 新規登録 |
| POST | /api/auth/login | ログイン（JWT発行） |

### 気分記録
| メソッド | パス | 説明 |
|---|---|---|
| POST | /api/moods/ | 気分を記録 |
| GET | /api/moods/ | 自分の記録一覧 |
| DELETE | /api/moods/{id} | 記録を削除 |

### 価値観
| メソッド | パス | 説明 |
|---|---|---|
| GET | /api/values/ | 価値観マスター一覧 |
| GET | /api/values/me | 自分が選んだ価値観 |
| POST | /api/values/me | 価値観を選択 |
| DELETE | /api/values/me/{value_id} | 選択を解除 |

### 実践
| メソッド | パス | 説明 |
|---|---|---|
| GET | /api/practices/ | 実践メニュー一覧 |
| POST | /api/practices/logs | 実践を記録 |
| GET | /api/practices/logs | 自分の実践ログ |

---

## Supabase 接続設定

1. Supabase プロジェクトを作成
2. Settings > Database > Connection String (URI) をコピー
3. `.env` の `DATABASE_URL` に設定（`postgresql+asyncpg://` プレフィックスに変更）

```
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

---

## デプロイ（Vercel + Railway / Render）

バックエンドは Vercel Functions または Railway / Render へデプロイ可能です。
`Dockerfile` を利用してコンテナデプロイも対応しています。

> **注意：** 本番環境では必ず `SECRET_KEY` を強力なランダム文字列に変更してください。
