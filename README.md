# Image Upscale Service with Flask and Celery

### 📋 Requirements Completed
- **POST /upscale** - Upload image, returns task ID
- **GET /tasks/<task_id>** - Check status and get download URL  
- **GET /processed/<filename>** - Download processed image
- **Singleton pattern** - Model loads only once
- **In-memory processing** - No intermediate disk saves
- **Docker configuration** - Ready for containerization
- **Tests included** - test_app.py

### Quick Start

#### 1. Install Dependencies
```bash
pip install -r requirements.txt