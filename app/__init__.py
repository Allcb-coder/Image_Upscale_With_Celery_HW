from flask import Flask
from .celery_app import make_celery

celery = None

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize Celery
    global celery
    celery = make_celery(app)

    # Import and register blueprints
    from .main import main_bp
    app.register_blueprint(main_bp)

    return app