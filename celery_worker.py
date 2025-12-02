import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Celery app
from celery_app import celery_app

if __name__ == '__main__':
    print("🔄 Starting Celery worker...")
    print(f"📡 Broker: {celery_app.conf.broker_url}")
    print(f"💾 Backend: {celery_app.conf.result_backend}")
    
    argv = [
        'worker',
        '--loglevel=info',
        '--concurrency=1'
    ]
    celery_app.worker_main(argv)
