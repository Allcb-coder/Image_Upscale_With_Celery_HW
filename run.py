import os
from app import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Image Upscale Service")
    print(f"📁 Model: {'✅ Found' if os.path.exists('EDSR_x2.pb') else '❌ Missing'}")
    print(f"🌐 Server: http://localhost:5000")
    print(f"🔗 Redis: {app.config['CELERY_BROKER_URL']}")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Processed folder: {app.config['PROCESSED_FOLDER']}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
