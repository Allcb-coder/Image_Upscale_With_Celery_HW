from celery import Celery
import os

def make_celery(app_name=__name__):
    celery_app = Celery(
        app_name,
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )

    celery_app.conf.update(
        task_serializer='pickle',
        accept_content=['pickle', 'json'],
        result_serializer='pickle',
        result_expires=3600,
        task_track_started=True,
    )

    return celery_app

# Create instance
celery_app = make_celery()