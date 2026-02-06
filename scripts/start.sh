#!/bin/bash
set -e

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start application
echo "Starting application with Gunicorn..."
exec gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
