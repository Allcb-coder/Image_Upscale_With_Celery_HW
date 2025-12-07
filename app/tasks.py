from app import celery  # Import from app.__init__

@celery.task(bind=True)
def upscale_image_task(self, image_path, original_filename):
    """Simple task for now - fix later"""
    return {
        'status': 'success',
        'message': 'Task received',
        'image_path': image_path
    }