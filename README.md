# Personalized RSS Feed Backend

Backend for a personalized social network aggregator. Built with FastAPI, PostgreSQL, Redis, and Celery.

## Features
- **User Management**: Ingestion of JWT Auth.
- **Source Management**: RSS, Blogs (HTML), YouTube Channels/Playlists.
- **Content Ingestion**: Strategy Enforced (RSS, Scraper, YouTube).
- **Feed**: Aggregated feed with deduplication.
- **Workers**: Celery for background fetching and scheduling.

## Tech Stack
- Python 3.11
- FastAPI
- SQLAlchemy (Async) + Alembic
- PostgreSQL (Supabase)
- Redis
- Celery

## Setup & Run (Simple / Local)

### 1. Prerequisites
- Python 3.11+
- Redis (Running locally or a cloud instance)
- Supabase Project (for PostgreSQL)

### 2. Environment
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` and fill in your Supabase connection string:
```bash
DATABASE_URL="postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
REDIS_URL="redis://localhost:6379/0" # Or your cloud Redis URL
```

### 3. Installation
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Migrations (Supabase)
Run migrations to create tables in your Supabase database:
```bash
alembic upgrade head
```

### 5. Run Application
Start the API server:
```bash
uvicorn app.main:app --reload
```

### 6. Run Worker
Start the Celery worker in a separate terminal:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## API Documentation
Once running, access the interactive API docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Deployment (Render)
This project is configured for easy deployment on Render.
1. Create a **Web Service** on Render connected to this repo.
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `./scripts/start.sh`
   - Env Vars: Add `DATABASE_URL` (your Supabase Connection String), `SECRET_KEY`, etc.
2. Create a **Reddis** instance on Render (or use an external one).
3. Create a **Background Worker** on Render for Celery.
   - Start Command: `./scripts/worker_start.sh`
