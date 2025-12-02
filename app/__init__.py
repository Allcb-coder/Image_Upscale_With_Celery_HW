from flask import Flask
from app.config import Config

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Register blueprints/routes
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
