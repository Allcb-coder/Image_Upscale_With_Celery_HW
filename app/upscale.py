import cv2
import os
import numpy as np
from app.config import Config


def upscale_image(input_path, output_path, scale=2):
    """
    Upscale image using EDSR model or OpenCV fallback
    """
    try:
        # Read image
        img = cv2.imread(input_path)
        if img is None:
            print(f"Error: Could not read image {input_path}")
            return False

        # Method 1: Try EDSR model if available
        if os.path.exists(Config.MODEL_PATH):
            print("Using EDSR model for upscaling")
            upscaled = upscale_with_edsr(img, Config.MODEL_PATH, scale)
        else:
            # Method 2: Fallback to OpenCV
            print("EDSR model not found, using OpenCV interpolation")
            height, width = img.shape[:2]
            upscaled = cv2.resize(
                img,
                (width * scale, height * scale),
                interpolation=cv2.INTER_CUBIC
            )

        # Save result
        cv2.imwrite(output_path, upscaled)
        print(f"Upscaled image saved to {output_path}")
        return True

    except Exception as e:
        print(f"Error in upscale_image: {e}")
        return False


def upscale_with_edsr(img, model_path, scale=2):
    """
    Upscale using EDSR model (you'll need to implement this based on your model format)
    """
    # This is a placeholder - implement based on your EDSR_x2.pb model
    # If it's a TensorFlow model:
    # import tensorflow as tf
    # model = tf.saved_model.load(model_path)
    # result = model(img)

    # For now, use OpenCV as fallback
    height, width = img.shape[:2]
    return cv2.resize(img, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)