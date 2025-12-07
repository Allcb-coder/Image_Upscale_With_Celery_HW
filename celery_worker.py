from app import create_app, celery

app = create_app()

if __name__ == '__main__':
    # This starts the Celery worker
    celery.start()