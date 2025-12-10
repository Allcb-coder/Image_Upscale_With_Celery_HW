from app.celery_app import celery_app
import app.tasks

if __name__ == '__main__':
    celery_app.start()