import os

from celery import Celery

CELERY_BACKEND = "redis://redis:6379/0"
BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

app = Celery(
    "app", broker=BROKER_URL, backend=CELERY_BACKEND, include=["celery_tasks.tasks"]
)
