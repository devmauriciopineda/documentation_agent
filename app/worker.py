import os

from celery import Celery

CELERY_BACKEND = "redis://redis-dev:6380/0"

broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

app = Celery("app", broker=broker_url, backend=CELERY_BACKEND, include=["app.tasks"])
