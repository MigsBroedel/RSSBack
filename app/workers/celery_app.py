from celery import Celery
from app.core.config import settings

# Redis URL string construction
redis_url = settings.REDIS_URL

celery_app = Celery("worker", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)

# Autodiscover tasks
celery_app.autodiscover_tasks(["app.workers"])
