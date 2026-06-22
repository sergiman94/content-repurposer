"""Celery application configuration."""

from celery import Celery

from backend.config import get_settings

settings = get_settings()

app = Celery(
    "content_repurposer",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["backend.worker.tasks"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
