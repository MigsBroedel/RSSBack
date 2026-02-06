#!/bin/bash
set -e

# Start celery worker
echo "Starting Celery worker..."
celery -A app.workers.celery_app worker --loglevel=info
