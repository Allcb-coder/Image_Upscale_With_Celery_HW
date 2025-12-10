from app.celery_app import celery_app
import uuid

@celery_app.task(bind=True, name='upscale_image_task')
def upscale_image_task(self, image_bytes: bytes, original_filename: str):
    """ONLY TASK - NO DISK SAVING"""
    try:
        from app.upscale import upscaler

        if not upscaler.is_ready:
            raise RuntimeError("Model not loaded")

        # Upscale in memory
        upscaled_bytes = upscaler.upscale(image_bytes)

        if upscaled_bytes is None:
            raise ValueError("Failed to upscale image")

        # Return bytes - stored in Redis
        return {
            'status': 'success',
            'image_bytes': upscaled_bytes,
            'filename': f"upscaled_{uuid.uuid4().hex}.png",
            'message': 'Image upscaled 2x using EDSR'
        }

    except Exception as e:
        raise RuntimeError(f"Upscaling failed: {str(e)}")