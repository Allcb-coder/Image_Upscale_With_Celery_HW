import cv2
import numpy as np
from typing import Optional
import os

class Upscaler:
    """Singleton for upscaling images"""
    _instance = None
    _model = None
    _model_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Upscaler, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance
    
    def _initialize_model(self):
        """Load model once"""
        try:
            # Check multiple possible locations
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'EDSR_x2.pb'),
                os.path.join(os.path.dirname(__file__), 'EDSR_x2.pb'),
                'EDSR_x2.pb',
                os.path.abspath('EDSR_x2.pb')
            ]
            
            model_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if model_path:
                print(f"Loading model from: {model_path}")
                self._model = cv2.dnn_superres.DnnSuperResImpl_create()
                self._model.readModel(model_path)
                self._model.setModel("edsr", 2)
                self._model_loaded = True
                print("✅ Model loaded successfully")
            else:
                print("⚠️  Model file not found")
                self._model_loaded = False
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self._model_loaded = False
    
    @property
    def is_ready(self):
        """Check if model is ready"""
        return self._model_loaded and self._model is not None
    
    def upscale(self, image_data: bytes) -> Optional[bytes]:
        """Upscale image from bytes (in-memory)"""
        if not self.is_ready:
            print("Model not ready, trying to initialize...")
            self._initialize_model()
            if not self.is_ready:
                return None
        
        try:
            # Convert bytes to image
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                print("Failed to decode image")
                return None
            
            print(f"Original size: {img.shape}")
            
            # Upscale
            result = self._model.upsample(img)
            print(f"Upscaled size: {result.shape}")
            
            # Encode back to bytes
            success, encoded_img = cv2.imencode('.png', result)
            if not success:
                return None
            
            return encoded_img.tobytes()
            
        except Exception as e:
            print(f"Upscaling error: {e}")
            return None

# Global instance
upscaler = Upscaler()
