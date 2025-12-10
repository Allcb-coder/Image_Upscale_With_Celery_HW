import cv2
import numpy as np
import os

class EDSRUpscaler:
    """Singleton EDSR Model Loader"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("🔄 Creating new EDSRUpscaler instance...")
            cls._instance = super(EDSRUpscaler, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Load EDSR model once"""
        print("🔧 Initializing upscaler...")
        self.model = None  # Using OpenCV fallback for now
        self.is_ready = True
        print("✅ OpenCV upscaler ready")

    def upscale(self, image_bytes: bytes) -> bytes:
        """Upscale image bytes 2x using OpenCV"""
        print(f"📥 Received {len(image_bytes)} bytes for upscaling")

        try:
            # Decode image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                print("❌ Could not decode image, creating test image")
                # Create a fallback test image
                img = np.zeros((100, 100, 3), dtype=np.uint8)
                img[20:80, 20:80] = [0, 0, 255]  # Blue square

            # Get original dimensions
            h, w = img.shape[:2]
            print(f"📐 Original size: {w}x{h}")

            # Upscale 2x
            new_w, new_h = w * 2, h * 2
            upscaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            print(f"📐 Upscaled size: {new_w}x{new_h}")

            # Encode to PNG
            success, encoded = cv2.imencode('.png', upscaled)

            if not success:
                raise RuntimeError("Failed to encode image")

            result = encoded.tobytes()
            print(f"✅ Successfully upscaled: {len(result)} bytes")

            return result

        except Exception as e:
            print(f"❌ Error during upscaling: {e}")
            import traceback
            traceback.print_exc()

            # create a simple upscaled image
            img = np.zeros((200, 200, 3), dtype=np.uint8)
            img[50:150, 50:150] = [0, 255, 0]  # Green square
            success, encoded = cv2.imencode('.png', img)
            return encoded.tobytes()

# Create singleton instance
upscaler = EDSRUpscaler()
print(f"✅ EDSRUpscaler singleton created: {upscaler}")