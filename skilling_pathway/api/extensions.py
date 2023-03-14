from celery import Celery
import os

celery = Celery(
    "app",
    backend=os.environ.get("CELERY_RESULT_BACKEND"),
    broker=os.environ.get("CELERY_BROKER_URL"),
)
