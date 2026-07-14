# Personalized Feed Aggregator — Backend

Backend for a personalized content aggregator: a user subscribes to heterogeneous sources — RSS feeds, HTML blogs, and YouTube channels/playlists — and gets a single deduplicated feed, kept fresh by background workers.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)
![Celery](https://img.shields.io/badge/Celery-workers-37814A)
![Redis](https://img.shields.io/badge/Redis-broker-DC382D)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-async-336791)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## About

The problem: content people care about is scattered across formats that don't share a protocol — some sources expose clean RSS, others only render HTML, others live behind the YouTube API. This backend normalizes all of them into one timeline.

Each source type has its own **ingestion strategy** (feed parser, HTML scraper, or YouTube fetcher) behind a common interface, so adding a new source kind is a matter of implementing one strategy rather than touching the aggregation logic. Fetching runs **asynchronously end-to-end** (async SQLAlchemy + httpx), and the heavy, scheduled work — polling sources, pulling new items, deduplicating — is offloaded to **Celery workers** brokered by **Redis**, keeping the API responsive. Retries on flaky sources are handled with `tenacity`.

This is the stack I reach for by default for backend work, and the project exists to exercise it end to end: async I/O, a worker queue, migrations, and JWT auth.

## Stack

- **Python 3.11**, **FastAPI**
- **SQLAlchemy (async)** + **Alembic** migrations
- **PostgreSQL** (Supabase) · **Redis** · **Celery**
- `feedparser`, `beautifulsoup4`, `lxml` — ingestion
- `python-jose` + `passlib[bcrypt]` — JWT auth
- `httpx`, `tenacity` — resilient fetching

## Architecture

```
app/
├── main.py            → FastAPI app
├── api/               → routes (auth, sources, feed)
├── ingestion/         → strategies: RSS · HTML scraper · YouTube
├── workers/           → Celery app + scheduled fetch tasks
├── models / db        → async SQLAlchemy + Alembic
alembic/               → migrations
scripts/               → start.sh, worker_start.sh (Render)
```

Request path: API writes source subscriptions → Celery beat schedules fetches → workers ingest via the matching strategy → items are deduplicated and persisted → the API serves the aggregated feed.

## Running locally

### Prerequisites
- Python 3.11+, Redis running locally, a PostgreSQL/Supabase database

### Setup
```bash
cp .env.example .env      # set DATABASE_URL and REDIS_URL
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

### Run
```bash
uvicorn app.main:app --reload                                   # API  → http://localhost:8000/docs
celery -A app.workers.celery_app worker --loglevel=info         # worker (separate terminal)
```

Interactive docs at `/docs` (Swagger) and `/redoc`.

## Deployment (Render)

Configured via `render.yaml`: a **Web Service** (`./scripts/start.sh`), a **Redis** instance, and a **Background Worker** for Celery (`./scripts/worker_start.sh`). Set `DATABASE_URL`, `REDIS_URL`, and `SECRET_KEY` as environment variables.

## Known limitations & roadmap

- No automated test suite yet — integration tests around the ingestion strategies are the priority.
- Deduplication is content/URL based; a fuzzy near-duplicate pass would improve quality.
- Roadmap: per-source health metrics, user-defined refresh intervals, and full-text search over the feed.

## License

MIT
