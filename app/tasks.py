from celery import Celery
from flask import current_app
import uuid
import os

def make_celery(app):
    """Create Celery app"""
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Register task here
    @celery.task(bind=True, name='upscale_image_task')
    def upscale_image_task(self, image_bytes: bytes, original_filename: str):
        """Celery task to upscale image"""
        # Import here to avoid circular imports
        from app.upscale import upscaler
        
        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'current': 25, 'total': 100, 'status': 'Processing started'}
        )
        
        try:
            print(f"Starting upscale for: {original_filename}")
            
            # Check model
            if not upscaler.is_ready:
                raise RuntimeError("Model not loaded")
            
            self.update_state(
                state='PROCESSING',
                meta={'current': 50, 'total': 100, 'status': 'Upscaling image'}
            )
            
            # Upscale
            upscaled_bytes = upscaler.upscale(image_bytes)
            
            if upscaled_bytes is None:
                raise ValueError("Failed to upscale image")
            
            # Generate filename
            processed_filename = f"upscaled_{uuid.uuid4().hex}.png"
            processed_path = os.path.join(
                current_app.config['PROCESSED_FOLDER'],
                processed_filename
            )
            
            # Save
            with open(processed_path, 'wb') as f:
                f.write(upscaled_bytes)
            
            print(f"Saved to: {processed_path}")
            
            self.update_state(
                state='SUCCESS',
                meta={
                    'current': 100,
                    'total': 100,
                    'status': 'Complete',
                    'filename': processed_filename
                }
            )
            
            return processed_filename
            
        except Exception as e:
            self.update_state(
                state='FAILURE',
                meta={
                    'current': 100,
                    'total': 100,
                    'status': 'Failed',
                    'error': str(e)
                }
            )
            raise
    
    return celery
