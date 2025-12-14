"""Celery application configuration."""

from celery import Celery
from core.config import settings

# Create Celery app
celery_app = Celery(
    "audio_processing",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "workers.transcription",
        "workers.translation",
        "workers.subtitle"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
)

# Task routing (optional - can be used to send different tasks to different queues)
celery_app.conf.task_routes = {
    "workers.transcription.*": {"queue": "transcription"},
    "workers.translation.*": {"queue": "translation"},
    "workers.subtitle.*": {"queue": "subtitle"},
}

if __name__ == "__main__":
    celery_app.start()