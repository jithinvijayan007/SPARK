from celery import Celery
import os
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

celery = Celery(
    "app",
    backend=os.environ.get("CELERY_RESULT_BACKEND"),
    broker=os.environ.get("CELERY_BROKER_URL"),
)
