from celery import Celery
import os

# Create Celery app
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True, name='upscale_image_task')
def upscale_image_task(self, image_bytes: bytes, original_filename: str):
    """Celery task to upscale image"""
    # Import here to avoid circular imports
    from app.upscale import upscaler
    import uuid
    
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
        
        # Use fixed path (since we don't have Flask context)
        processed_folder = os.path.join(os.getcwd(), 'static', 'processed')
        os.makedirs(processed_folder, exist_ok=True)
        processed_path = os.path.join(processed_folder, processed_filename)
        
        # Save
        with open(processed_path, 'wb') as f:
            f.write(upscaled_bytes)
        
        print(f"✅ Saved to: {processed_path}")
        
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
        print(f"❌ Task failed: {e}")
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
