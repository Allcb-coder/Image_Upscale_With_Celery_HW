import requests
import base64
import io
from PIL import Image

task_id = "0b82ebc6-3c43-4a38-9c94-4b0fdfb06ae2"

print("🔧 Fixing download issue...")

# First, let's get the task result directly from Celery
print("\n1. Getting task info...")
resp = requests.get(f'http://localhost:5000/tasks/{task_id}')
task_info = resp.json()
print(f"   Task state: {task_info['state']}")

# Try to access the processed endpoint
print("\n2. Trying processed endpoint...")
resp = requests.get(f'http://localhost:5000/processed/{task_id}')
print(f"   Status code: {resp.status_code}")
print(f"   Response: {resp.text[:200]}...")

# Alternative: Manually get and save the image
print("\n3. Manual workaround - checking if we can get bytes another way...")

# The task succeeded, so we know bytes exist in Redis
# Let's create a simple endpoint to test
print("\n4. Creating test script to extract bytes...")

# Create a test Flask app to extract bytes
from flask import Flask, jsonify
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Import Celery
from celery_worker_simple import celery_app

with app.app_context():
    task = celery_app.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        result = task.result
        print(f"\n✅ Task result keys: {list(result.keys())}")
        print(f"   Has 'image_bytes': {'image_bytes' in result}")
        
        if 'image_bytes' in result:
            image_bytes = result['image_bytes']
            print(f"   Image bytes type: {type(image_bytes)}")
            print(f"   Image bytes length: {len(image_bytes)}")
            
            # Save to file
            with open('manual_fix.png', 'wb') as f:
                f.write(image_bytes)
            print(f"✅ Saved to: manual_fix.png")
            
            # Verify it's a valid PNG
            try:
                img = Image.open('manual_fix.png')
                print(f"✅ Valid PNG: {img.size}")
                img.close()
            except Exception as e:
                print(f"❌ Not a valid image: {e}")
        else:
            print(f"❌ No 'image_bytes' in result")
    else:
        print(f"❌ Task not successful: {task.state}")
