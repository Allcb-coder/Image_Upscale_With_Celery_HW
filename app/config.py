import os


class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

    # Redis is already running on your machine
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # File paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
    RESULT_FOLDER = os.path.join(BASE_DIR, '..', 'results')
    MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'EDSR_x2.pb')

    # Create folders if they don't exist
    for folder in [UPLOAD_FOLDER, RESULT_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}