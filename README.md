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
- PostgreSQL
- Redis
- Celery
- Docker

## Setup & Run

### 1. Environment
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` if necessary.

### 2. Run with Docker
Build and start the services:
```bash
docker-compose up --build
```

### 3. Migrations
Once the database is up, run migrations to create tables:
```bash
# This needs to be run from within the api container or having access to the DB
docker-compose exec api alembic upgrade head
```

## API Documentation
Once running, access the interactive API docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Development
- `app/services/ingestion/`: Contains the logic for fetching content.
- `app/workers/`: Contains Celery tasks.
